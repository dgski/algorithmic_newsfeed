<script>
	import { onMount } from 'svelte'
	import Story from './Story.svelte'

	let name = 'world';
	let stories = []
	const API_URL = 'http://localhost:5000/'
	let holder;

	let requestInProgress = false
	function requestNext() {
		if(requestInProgress) {
			return
		}
		requestInProgress = true
		fetch(API_URL + 'documents')
		.then(response => {
			if(response.ok) {
				return response.json()
			}
		})
		.then(data => {
			console.log(data)
			stories = stories.concat(data)
			requestInProgress = false
		})
	}

	onMount(() => {
		requestNext()
		console.log(holder)
		window.onscroll = () => {
			const docElem = document.documentElement
			if((docElem.scrollHeight - (docElem.scrollTop + docElem.clientHeight)) < 100) {
				requestNext()
			}
		}
	})

	function openAddFeedDialog() {
		let response = prompt("Paste feed URL:")
		if(response != null) {
			console.log(response)
			fetch(API_URL + 'add-feed?feed=' + response)
			.then(r => {
				if(r.ok) {
					alert("Feed Added Succesfully");
				} else {
					alert("Problem adding feed.");
				}
			})
		}
	}
</script>

<style>
	:global(body) {
		margin: 0 !important;
		padding: 0;
	}

	#header {
		background-color: steelblue;
		color: white;
		text-align: center;
		font-size: 32px;
		padding: 30px;
	}

	#header button {
		font-size: 13px;
		margin: 10px;
	}

	#holder {
		width: 500px;
		margin-left: calc(50% - 250px);
		font-size: 12px;
	}

	:global(img, video) {
    	width: 100%;
		display: block;
	}
</style>

<div id="header">
	Algorithmic Feed <button on:click={openAddFeedDialog}>Add To Feed</button>
</div>

<div id="holder" bind:this={holder}>
	{#each stories as story}
		<Story {story}></Story>
	{/each}
</div>

