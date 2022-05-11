import json
from pathlib import Path
from typing import List

from fastcore.net import HTTP4xxClientError
from ghapi.all import GhApi, paged


PAT_FILE = Path(__file__, '..', 'GITHUB_TOKEN.json').resolve()
PAT = ''
with PAT_FILE.open('r', encoding='utf-8') as pat_fp:
    PAT = json.load(pat_fp)['PAT']
if not PAT:
    raise ValueError('Cannot find your Personal Access Token (PAT). We expect'
                     f' the PAT token to be in the {PAT_FILE} file, as the '
                     'value to the key named "PAT".')


api = GhApi(owner="UCREL", repo="pymusas-models", token=PAT)

print(f'Current rate limit: {api.rate_limit.get()["rate"]}\n\n')


tag_names_uploaded: List[str] = []


models_folder = Path(__file__, '..', 'models').resolve()
for model_folder in models_folder.iterdir():
    tag_name = model_folder.name
    readme_text = ''
    with Path(model_folder, 'README.md').open('r', encoding='utf-8') as readme_fp:
        readme_text = readme_fp.read()

    model_assets = [str(asset_file_name) for asset_file_name in Path(model_folder, 'dist').iterdir()]
    try:
        api.create_release(tag_name=tag_name, branch='main', name=tag_name,
                           body=readme_text, draft=False, prerelease=False,
                           files=model_assets)
    except HTTP4xxClientError:
        print('This exception most likely occurs due to the release for '
              f'{tag_name} already existing as a release:')
        raise
    except Exception:
        print(f'Unknown exception has occurred for {tag_name}:')
        raise
    tag_names_uploaded.append(tag_name)

tag_names_uploaded_set = set(tag_names_uploaded)
if len(tag_names_uploaded_set) != len(tag_names_uploaded):
    identical_tag_name_error = ('There are model folders that have the same'
                                f'name within {models_folder}, all model '
                                'folders have to have unique model folder'
                                'names.')
    raise ValueError(identical_tag_name_error)


release_pages = paged(api.repos.list_releases, per_page=100)
for release_page in release_pages:
    for release in release_page:
        assert release.name == release.tag_name
        
        assert 2 == len(release.assets)
        allowed_asset_names: List[str] = []
        allowed_asset_names.append(f'{release.tag_name}-py3-none-any.whl')
        allowed_asset_names.append(f'{release.tag_name}.tar.gz')
        for asset in release.assets:
            if asset.name in allowed_asset_names:
                allowed_asset_names.remove(asset.name)
        assert not allowed_asset_names

        if release.tag_name in tag_names_uploaded_set:
            tag_names_uploaded_set.remove(release.tag_name)

if tag_names_uploaded_set:
    raise Exception('Not all of the model were released. Models that were not'
                    f' released are the following:\n{tag_names_uploaded_set}')

print(f'\n\nRate limit after model releases: {api.rate_limit.get()["rate"]}')
