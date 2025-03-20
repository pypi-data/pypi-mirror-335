// package.json
var name = "anywidget";
var version = "0.4.3";

// src/widget.js
function is_href(str) {
  return str.startsWith("http://") || str.startsWith("https://");
}
async function load_css_href(href, anywidget_id) {
  let prev = document.querySelector(`link[id='${anywidget_id}']`);
  if (prev) {
    let newLink = (
      /** @type {HTMLLinkElement} */
      prev.cloneNode()
    );
    newLink.href = href;
    newLink.addEventListener("load", () => prev?.remove());
    prev.after(newLink);
    return;
  }
  return new Promise((resolve) => {
    let link = Object.assign(document.createElement("link"), {
      rel: "stylesheet",
      href,
      onload: resolve
    });
    document.head.appendChild(link);
  });
}
function load_css_text(css_text, anywidget_id) {
  let prev = document.querySelector(`style[id='${anywidget_id}']`);
  if (prev) {
    prev.textContent = css_text;
    return;
  }
  let style = Object.assign(document.createElement("style"), {
    id: anywidget_id,
    type: "text/css"
  });
  style.appendChild(document.createTextNode(css_text));
  document.head.appendChild(style);
}
async function load_css(css, anywidget_id) {
  if (!css)
    return;
  if (is_href(css))
    return load_css_href(css, anywidget_id);
  return load_css_text(css, anywidget_id);
}
async function load_esm(esm) {
  if (is_href(esm)) {
    return import(
      /* webpackIgnore: true */
      esm
    );
  }
  let url = URL.createObjectURL(
    new Blob([esm], { type: "text/javascript" })
  );
  let widget;
  try {
    widget = await import(
      /* webpackIgnore: true */
      url
    );
  } catch (e) {
    console.log(e);
    throw e;
  }
  URL.revokeObjectURL(url);
  return widget;
}
function widget_default(base) {
  class AnyModel extends base.DOMWidgetModel {
    static model_name = "AnyModel";
    static model_module = name;
    static model_module_version = version;
    static view_name = "AnyView";
    static view_module = name;
    static view_module_version = version;
    /** @param {Parameters<InstanceType<base["DOMWidgetModel"]>["initialize"]>} args */
    initialize(...args) {
      super.initialize(...args);
      this.on("change:_css", () => {
        let id = this.get("_anywidget_id");
        if (!id)
          return;
        console.debug(`[anywidget] css hot updated: ${id}`);
        load_css(this.get("_css"), id);
      });
      this.on("change:_esm", async () => {
        let id = this.get("_anywidget_id");
        if (!id)
          return;
        console.debug(`[anywidget] esm hot updated: ${id}`);
        let views = (
          /** @type {Promise<AnyView>[]} */
          Object.values(this.views ?? {})
        );
        for await (let view of views) {
          let widget = await load_esm(this.get("_esm"));
          await view._anywidget_cached_cleanup();
          view.$el.empty();
          view.stopListening(this);
          let cleanup = await widget.render(view);
          view._anywidget_cached_cleanup = cleanup ?? (() => {
          });
        }
      });
    }
  }
  class AnyView extends base.DOMWidgetView {
    async render() {
      await load_css(this.model.get("_css"), this.model.get("_anywidget_id"));
      let widget = await load_esm(this.model.get("_esm"));
      let cleanup = await widget.render(this);
      this._anywidget_cached_cleanup = cleanup ?? (() => {
      });
    }
    /** @type {() => Promise<void> | void} */
    _anywidget_cached_cleanup() {
    }
    async remove() {
      await this._anywidget_cached_cleanup();
      return super.remove();
    }
  }
  return { AnyModel, AnyView };
}

// src/index.js
define(["@jupyter-widgets/base"], widget_default);
