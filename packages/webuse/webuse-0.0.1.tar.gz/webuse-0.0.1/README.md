# Web-use

`webuse` is a http request library and a minimal headless browser, wrapped with the AI
buzzword -- the "Agent".

It can perform web-based actions on your command with natural languages, on par with
other "agent" libraries like `browser-use` or `computer-use`, but at a smaller
footprint.

As a project from the author of `curl-cffi`, `webuse` was built with impersonating human
behavior at the very beginning. So unlike other academic focused projects, `webuse`
tends to have lower rate of being detected as bot by `WAF`s like Cloudflare. In real
world, everyone have the same LLMs, such as ChatGPT, Claude and DeepSeek, so the
ability to mimic human behavior becomes the key differentiator for success rate.

This is a opinionated library, we only support certain preferred tools at core. However,
feel free to contribute and maintain your flavor.

## Features(to be implemented)

1. Execute JavaScript directly, like `pyexecjs`, but via API.
    - Pass a piece of script and execute directly.
    - Register a script to be called later via name or id.
    - Create virtual env with custom patches.
2. Use JS RPC to call the algorithm on host page.
    - Execute functions directly within the page context.
    - Register additional scripts to the page.
3. Docker image for one-click install as a service.
4. Call webuse as a headless browser, without the `webdriver` attributes.
    - Integrate common anti-detect scripts from [Undetected chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
    - Generate random values for JS based fingerprints.

## Usage

```sh
pip install webuse
```

On Linux servers, it's best to run this with `xvfbwrapper`

The main interface is a simple webbrowser-like UI for debuggin purposes. Once started,
A HTTP API will be exposed for you to interact with cute agent.

When a render request is submitted, a tab will be selected to render the page, once finished,
the content will be cached to a pool, waiting for retrieval, and the tab will be recycled.

The cache will be removed after a given time or once it is retrieved.


### Headless browser

You do not need to create a patched environment to emulate the browser,
because it's indeed a real WebKit based browser. On the other hand, it's built for
crawling, not testing. It's much easier to manage a wkenv service than a Playwright or
Selenium service.


## TODO

- [ ] Make the UI better, more browser-like
- [x] Add mulitple webview for parallelized rendering
- [ ] Add lock when a webview is occupied for rendering
- [ ] When all tabs are being used, return a busy error
- [ ] Add a pool for caching rendered content
- [ ] Add a busy wait endpoint for retrieving the content

Acknowledgements
------

PySide6 tutorial: https://www.pythonguis.com/pyqt6/
