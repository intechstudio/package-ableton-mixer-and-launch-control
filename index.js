const fs = require("fs");
const path = require("path");
const os = require("os");

let controller;
let preferenceMessagePort = undefined;

// Default Ableton User Library Remote Scripts path
function getAbletonScriptsPath() {
  const homedir = os.homedir();
  const platform = os.platform();

  if (platform === "darwin") {
    // macOS: /Users/[username]/Music/Ableton/User Library/Remote Scripts
    return path.join(
      homedir,
      "Music",
      "Ableton",
      "User Library",
      "Remote Scripts",
    );
  } else {
    // Windows: C:\Users\[username]\Documents\Ableton\User Library\Remote Scripts
    return path.join(
      homedir,
      "Documents",
      "Ableton",
      "User Library",
      "Remote Scripts",
    );
  }
}

function getScriptsFolders() {
  const scriptsPath = path.resolve(__dirname, "scripts");
  try {
    const entries = fs.readdirSync(scriptsPath, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name);
  } catch (error) {
    console.error("Error reading scripts folder:", error);
    return [];
  }
}

function copyFolderRecursive(source, destination) {
  // Create destination folder if it doesn't exist
  if (!fs.existsSync(destination)) {
    fs.mkdirSync(destination, { recursive: true });
  }

  const entries = fs.readdirSync(source, { withFileTypes: true });

  for (const entry of entries) {
    const sourcePath = path.join(source, entry.name);
    const destPath = path.join(destination, entry.name);

    if (entry.isDirectory()) {
      copyFolderRecursive(sourcePath, destPath);
    } else {
      fs.copyFileSync(sourcePath, destPath);
    }
  }
}

exports.loadPackage = async function (gridController, persistedData) {
  controller = gridController;
  console.log("Ableton Script Installer package loaded");
};

exports.unloadPackage = async function () {
  preferenceMessagePort?.close();
};

exports.addMessagePort = async function (port, senderId) {
  if (senderId == "preferences") {
    preferenceMessagePort?.close();
    preferenceMessagePort = port;

    port.on("close", () => {
      preferenceMessagePort = undefined;
    });

    port.on("message", (e) => {
      const data = e.data;
      console.log("Received message:", data);

      if (data.type === "get-folders") {
        const folders = getScriptsFolders();
        port.postMessage({
          type: "folders-list",
          folders: folders,
        });
      } else if (data.type === "install-script") {
        const folderName = data.folderName;
        const sourcePath = path.resolve(__dirname, "scripts", folderName);
        const destPath = path.join(
          getAbletonScriptsPath(),
          "Grid_mixer_launch_control",
        );

        try {
          // Check if source folder exists
          if (!fs.existsSync(sourcePath)) {
            const errorMsg = `Source folder not found: ${sourcePath}`;
            console.error(errorMsg);
            port.postMessage({
              type: "install-result",
              success: false,
              error: errorMsg,
              folderName: folderName,
            });
            return;
          }

          // Ensure the Remote Scripts folder exists
          const remoteScriptsPath = getAbletonScriptsPath();
          if (!fs.existsSync(remoteScriptsPath)) {
            fs.mkdirSync(remoteScriptsPath, { recursive: true });
          }

          // Remove existing destination folder if it exists
          if (fs.existsSync(destPath)) {
            fs.rmSync(destPath, { recursive: true, force: true });
          }

          // Copy the folder
          copyFolderRecursive(sourcePath, destPath);

          console.log(`Successfully installed ${folderName} to ${destPath}`);
          port.postMessage({
            type: "install-result",
            success: true,
            folderName: folderName,
            destPath: destPath,
          });

          // Also show a toast message in the Editor
          controller.sendMessageToEditor({
            type: "show-message",
            message: `Successfully installed ${folderName} to Ableton Remote Scripts folder!`,
            messageType: "success",
          });
        } catch (error) {
          const errorMsg = `Failed to install ${folderName}: ${error.message}`;
          console.error(errorMsg, error);
          port.postMessage({
            type: "install-result",
            success: false,
            error: errorMsg,
            folderName: folderName,
          });

          controller.sendMessageToEditor({
            type: "show-message",
            message: errorMsg,
            messageType: "fail",
          });
        }
      }
    });

    port.start();

    // Send initial folder list
    const folders = getScriptsFolders();
    port.postMessage({
      type: "folders-list",
      folders: folders,
    });
  }
};

exports.sendMessage = async function (args) {
  console.log("sendMessage received:", args);
};
