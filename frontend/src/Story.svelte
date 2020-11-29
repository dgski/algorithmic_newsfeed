<script>
    export let story;
    const API_URL = 'http://localhost:5000/'
    let similar_stories = undefined

    function getSimilar(post_id) {
		fetch(API_URL + 'similar/' + post_id)
		.then(response => {
			if(response.ok) {
				return response.json()
			}
		})
		.then(data => {
			similar_stories = data
		})
    }
    
    function markGood(post_id) {
        fetch(API_URL + 'report/good/' + post_id)
    }

    function markBad(post_id) {
        fetch(API_URL + 'report/bad/' + post_id)
    }
</script>

<style>
	.story {
		padding: 10px;
		padding-top: 20px;
		padding-bottom: 20px;
		border-bottom: 1px solid gainsboro;
	}

</style>

<div class="story">
    <h2>{story.title}</h2>
    <i>{story.published}</i>
    <p>{@html story.summary}</p>
    <button on:click={() => markGood(story.id)}>Good Suggestion</button>
    <button on:click={() => markBad(story.id)}>Bad Suggestion</button>
    <button on:click={() => getSimilar(story.id)}>More Stories Like This...</button>
    {#if similar_stories}
        <h3>Similar Stories</h3>
        <ul>
            {#each similar_stories as similar_story}
                <li><a href={similar_story.document.link}>{similar_story.document.title}</a>({similar_story.score})</li>
            {/each}
        </ul>
    {/if}
</div>