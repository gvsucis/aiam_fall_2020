function onExecuted(result) {
  console.log(`We made it green`);
}

function onError(error) {
  console.log(`Error: ${error}`);
}

let e;

document.addEventListener("click", async function(e) {
  if (!e.target.classList.contains("pop-content-enable-btn")) {
    return;
  }

  e = browser.tabs.executeScript({
    file: '/pathselector.js'
  });

  e.then( onExecuted, onError );

  console.log("loaded!");
});