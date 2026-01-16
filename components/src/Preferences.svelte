<svelte:options
  customElement={{ tag: "ableton-script-installer-preference", shadow: "none" }}
/>

<script>
  import {
    Block,
    BlockBody,
    BlockTitle,
    MoltenPushButton,
  } from "@intechstudio/grid-uikit";
  import { onMount } from "svelte";

  let folders = [];
  let statusMessage = "";
  let statusType = ""; // "success" or "error"
  let statusTimeoutId = null;

  // @ts-ignore
  const messagePort = createPackageMessagePort(
    "package-ableton-mixer-and-launch-control",
    "preferences",
  );

  function installScript(folderName) {
    statusMessage = `Installing ${folderName}...`;
    statusType = "";
    messagePort.postMessage({
      type: "install-script",
      folderName: folderName,
    });
  }

  onMount(() => {
    messagePort.onmessage = (e) => {
      const data = e.data;
      if (data.type === "folders-list") {
        folders = data.folders;
      } else if (data.type === "install-result") {
        if (data.success) {
          statusMessage = `Successfully installed ${data.folderName}!`;
          statusType = "success";
          // Clear any existing timeout
          if (statusTimeoutId) {
            clearTimeout(statusTimeoutId);
          }
          // Hide success message after 3 seconds
          statusTimeoutId = setTimeout(() => {
            statusMessage = "";
            statusType = "";
            statusTimeoutId = null;
          }, 3000);
        } else {
          statusMessage = `Error: ${data.error}`;
          statusType = "error";
          console.error("Install error:", data.error);
        }
      }
    };
    messagePort.start();

    // Request initial folder list
    messagePort.postMessage({ type: "get-folders" });

    return () => {
      if (statusTimeoutId) {
        clearTimeout(statusTimeoutId);
      }
      messagePort.close();
    };
  });
</script>

<main-app>
  <div class="px-4 bg-secondary rounded-lg">
    <Block>
      <BlockTitle>
        <div class="flex flex-row content-center">Ableton Script Installer</div>
      </BlockTitle>
      <BlockBody>
        <p class="text-gray-400 text-sm mb-4">
          Click a button to install the corresponding script to your Ableton
          User Library Remote Scripts folder.
        </p>

        {#if folders.length === 0}
          <p class="text-gray-500">No script folders found.</p>
        {:else}
          <div class="flex flex-col gap-2">
            {#each folders as folder}
              <MoltenPushButton
                click={() => installScript(folder)}
                text={`Install ${folder}`}
              />
            {/each}
          </div>
        {/if}

        <p class="mt-2 p-2 rounded text-sm">
          {statusMessage}
        </p>
      </BlockBody>
    </Block>
  </div>
</main-app>
