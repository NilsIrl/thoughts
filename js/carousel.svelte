<script lang="ts">
    export let prompt;
    export let selected_url = "";
    let selected = -1;

    let urls = fetch(`/api/images?prompt=${encodeURIComponent(prompt)}`, {
        method: "POST",
    }).then((response) => response.json());
</script>

<div>
    {#await urls}
        <span
            style="margin: 30px auto; display: block; width: 50px; height: 50px;"
            class="loader"
        />
    {:then images}
        {#if images["error"] }
            <p class="has-text-danger">{ images["error"] }</p>
        {:else}
            {#each images as image_url, i}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <img on:click="{e => {selected = i; selected_url = image_url}}" class:selected={i == selected} alt="prompt generated" src={image_url} />
            {/each}
        {/if}
    {:catch error}
        <p class="has-text-danger">There was an error with your prompt { error.message }</p>
    {/await}
</div>

<style>
    img {
        width: 23%;
    }
    .selected {
        width: 28%;
    }
</style>
