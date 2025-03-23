function toDisplay(b){
  return b? '' : 'none';
}

function toDate(date) {
  return new Date(date).toLocaleDateString('ja-JP');
}

function addRetry(target, updator, onError){
  const maxRetries = 10;
  const retryDelay = 500;
  let retries = 0;
  target.addEventListener('error', () => {
    if(retries < maxRetries){
      retries++;
      console.warn(`Retrying ${target._src} (${retries}/${maxRetries})`);
      setTimeout(() => {
        updator(retries);
      }, retryDelay);
    }
    else{
      console.error(`Failed to load media ${target._src} after ${maxRetries} retries.`);
      onError();
    }
  });
}

const observer = new IntersectionObserver((entries, obs) => {
  entries.forEach(entry => {
    if(!entry.isIntersecting)
    {
      return;
    }

    if(entry.target.tagName == 'IMG')
    {
      const img = entry.target;
      img.src = img._src;
      obs.unobserve(img);
    }
    else if (entry.target.tagName == 'VIDEO')
    {
      const video = entry.target;
      video.src = video._src;
      video.load();
      obs.unobserve(video);
    }
    else {
      console.warn(`[Observer] Unknown target ${entry.target.tagName}`);
    }
  });
});

function createVideoTile(src, displayName, width, notifier){
  const video = document.createElement('video');
  video.controls = true;
  video.autoplay = true;
  video.muted = true;
  video.loop = true;
  video.title = displayName;
  video._src = src;
  video.style.width = width;

  addRetry(video,
    retries => {
      video.src = `${src}?retry=${retries}`;
      video.load();
    },
    ()=>notifier.error(`Failed to load video. See the log for more info.`));

  observer.observe(video);

  updator = {
    tile: video,
    updateWidth: width => video.style.width = `${width}px`,
    updateVisibility: visibility => video.style.display = toDisplay(visibility),
  };

  return [video, updator];
}

function createTile(i, initialWidth, notifier)
{
  const src = `contents/${i.path}`;
  const ext = src.slice(src.lastIndexOf('.'));

  if([".mp4"].indexOf(ext) > -1){
    const a = document.createElement('a');
    a.className += 'modaalIframe';
    a.href = src;
    const [video, updator] = createVideoTile(src, i.displayName, initialWidth, notifier);
    a.appendChild(video);

    updator.tile = a;
    return updator;
  }
  else if([".mov"].indexOf(ext) > -1){
    const [video, updator] = createVideoTile(src, i.displayName, initialWidth, notifier);
    updator.tile = video;
    return updator;
  }
  else{
    const a = document.createElement('a');
    a.className += "modaalImage";
    a.setAttribute("data-group", "gallery");
    a.href = src;

    const img = document.createElement("img");
    img.style.width = `${initialWidth}px`;
    img.style.height = `${initialWidth}px`;
    img.style.objectFit = 'contain';
    img.style.backgroundColor = '#a5a5a5';
    img.style.boxShadow = 'inset 0 0 2px 1px white';
    img.title = i.displayName;
    img.loading = 'lazy';
    img._src = src;

    observer.observe(img);
    addRetry(img,
      retries => img.src = `${src}?retry=${retries}`,
      ()=>notifier.error(`Failed to load media. See the log for more info.`));

    img.addEventListener('load', ()=>{
      img.style.height = 'auto';
    });

    a.appendChild(img);

    return {
      tile: a,
      updateWidth: width => img.style.width = `${width}px`,
      updateVisibility: visibility => img.style.display = toDisplay(visibility),
    };
  }
}

function tileMedia(mediaList, initialWidth, notifier)
{
  return Object.fromEntries(mediaList.map(i => [i.path, createTile(i, initialWidth, notifier)]))
}

function setupModaal()
{
  $('.modaalImage').modaal({
    type: 'image',
    hide_close: true,
  })
  $('.modaalIframe').modaal({
    type: 'iframe',
    hide_close: true,
  });
}

class Notification {
  constructor(containerId = 'notificationContainer') {
    this.container = document.getElementById(containerId);
  }

  info(message)
  {
    console.log(message);
    this.show(message, 'info');
  }

  warn(message)
  {
    console.warn(message);
    this.show(message, 'warning');
  }

  error(message)
  {
    console.error(message);
    this.show(message, 'error', 5000);
  }

  show(message, type='info', duration=3000) {

    const notification = document.createElement('div');
    notification.classList.add('notification', type);
    notification.textContent = message;
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(20px)';

    this.container.appendChild(notification);

    requestAnimationFrame(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateX(0)';
    });

    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(20px)';
      setTimeout(() => notification.remove(), 500);
    }, duration);
  }
}

function createFcArticleUrl(board, contentId)
{
  return `https://girls2-fc.jp/page/${board}/${contentId}`;
}

function createMetadata(author, date, board, contentId) {
  const i = document.createElement('i');
  i.classList = ['fa fa-external-link'];

  const a = document.createElement('a');
  a.href = createFcArticleUrl(board, contentId);
  a.target = '_blank';
  a.appendChild(i);

  const div = document.createElement('div');
  div.appendChild(document.createTextNode(`${author} ${new Date(date).toLocaleDateString('ja-JP')} `));
  div.appendChild(a);
  div.style.fontSize = "0.8em";
  div.style.margin = '0';
  return div;
}

function createTitle(title, author, date, board, contentId) {
  const h = document.createElement('h1');
  h.appendChild(document.createTextNode(title));

  const container = document.createElement('div');
  container.appendChild(h);
  container.appendChild(createMetadata(author, date, board, contentId));
  return container;
}

function encodeParameter(state, defaultState)
{
  const params = new URLSearchParams();
  Object.entries(state).forEach(([k, v]) =>{
    if (v != defaultState[k]){
      params.append(k, v);
    }
  });
  return params.toString();
}

function decodeParameter(params, defaultState)
{
  const state = {...defaultState};
  new URLSearchParams(params).forEach((v, k) => {
    if(Object.prototype.hasOwnProperty.call(state, k)) {
      state[k] = v;
    }
  });
  return state;
}

function createContextMenuButton(title, command, canExecute) {
  const button = document.createElement('button');
  button.appendChild(document.createTextNode(title));
  button.onclick = command;
  button.style.whiteSpace = 'nowrap';
  if (!canExecute)
  {
    button.disabled = true;
  }
  return button;
}

function initCustomContextMenu(items, x, y) {
  tileContextMenu.replaceChildren();
  items.forEach(i => tileContextMenu.appendChild(i));

  const menuWidth = tileContextMenu.offsetWidth;
  const menuHeight = tileContextMenu.offsetHeight;

  const posX = x + menuWidth < window.innerWidth? x:x - menuWidth;
  const posY = y + menuHeight < window.innerHeight? y : y - menuHeight;

  tileContextMenu.style.top = `${posY}px`;
  tileContextMenu.style.left = `${posX}px`;
  tileContextMenu.style.display = 'block';
}

function isLocalFile() {
  return  window.location.protocol === 'file:';
}

function isHttp() {
  const protocol = window.location.protocol;
  return protocol === 'http:' || protocol === 'https:';
}

function isNarrow() {
  return window.innerWidth <= 960;
}
