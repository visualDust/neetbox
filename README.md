# NEETBOX

![](./docs/static/img/readme.png)

Python API, backend server, frontend, ALL IN ONE. A tool box for Logging/Debugging/Tracing/Managing/Facilitating long running python projects, especially a replacement of tensorboard for deep learning projects.

[![wakatime](https://wakatime.com/badge/user/b93a26b6-8ea1-44ef-99ed-bcb6e2c732f1/project/8f99904d-dbb1-49e4-814d-8d18bf1e6d1c.svg)](https://wakatime.com/badge/user/b93a26b6-8ea1-44ef-99ed-bcb6e2c732f1/project/8f99904d-dbb1-49e4-814d-8d18bf1e6d1c) [![pytest](https://github.com/visualDust/neetbox/actions/workflows/poetry-pytest.yml/badge.svg)](https://github.com/visualDust/neetbox/actions/workflows/poetry-pytest.yml) ![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/visualdust/neetbox/build-and-publish-pypi.yml) ![PyPI - Version](https://img.shields.io/pypi/v/neetbox)
 ![PyPI - Downloads](https://img.shields.io/pypi/dw/neetbox) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## screenshot

![](./docs/static/img/screenshot.jpg)

## dev

NEETBOX is under heavy development.

- [x] monit multi project on one dashboard
- [x] local/remote logging
- [x] command line cli tools
- [x] system monitoring
- [x] post images to frontend
- [ ] plotting(scatters, line chart...)
- [x] run python code by clicking on frontend buttons
- [x] history automatically saved by backend
- [ ] attach remote logging in command line cli
- [ ] distinguish different runs

## docs

[neetbox.550w.host](https://neetbox.550w.host). (APIs are ready but we are not ready for the doc yet)

## quick start

install neetbox:
```bash
pip install neetbox
```

in any python code folder:
```
neet init
```
neetbox cli generates a config file for your project named `neetbox.toml`

then in your code:
```python
import neetbox
```

run your code and visit https://localhost:20202 to see your dashboard.

## usage examples

[how to guides](todo) provides easy examples of basic neetbox funcionalities.

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://gavin.gong.host"><img src="https://avatars.githubusercontent.com/u/33346934?v=4?s=100" width="100px;" alt="Gavin Gong"/><br /><sub><b>Gavin Gong</b></sub></a><br /><a href="#projectManagement-visualDust" title="Project Management">📆</a> <a href="#code-visualDust" title="Code">💻</a> <a href="#doc-visualDust" title="Documentation">📖</a> <a href="#ideas-visualDust" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-visualDust" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-visualDust" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://yuuza.net"><img src="https://avatars.githubusercontent.com/u/14901890?v=4?s=100" width="100px;" alt="lideming"/><br /><sub><b>lideming</b></sub></a><br /><a href="#code-lideming" title="Code">💻</a> <a href="#design-lideming" title="Design">🎨</a> <a href="#infra-lideming" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-lideming" title="Maintenance">🚧</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=visualDust/neetbox&type=Date)](https://star-history.com/#visualDust/neetbox&Date)
