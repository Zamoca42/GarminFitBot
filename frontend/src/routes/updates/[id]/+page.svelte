<script lang="ts">
	import { marked } from 'marked';
	import { goto } from '$app/navigation';

	export let data;

	$: updateItem = data.update;
	let isLoading = false;
	let error = '';

	function goBack() {
		goto('/updates');
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('ko-KR', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	marked.setOptions({
		breaks: true,
		gfm: true
	});
</script>

<svelte:head>
	<title>{updateItem ? `${updateItem.title} - GarminFitBot` : '업데이트 내역 - GarminFitBot'}</title
	>
</svelte:head>

<div class="py-12">
	<div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
		<div class="mb-6">
			<button class="flex items-center text-indigo-600 hover:text-indigo-700" on:click={goBack}>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="mr-2 h-5 w-5"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<path
						fill-rule="evenodd"
						d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
						clip-rule="evenodd"
					/>
				</svg>
				모든 업데이트 보기
			</button>
		</div>

		{#if isLoading}
			<div class="flex items-center justify-center py-12">
				<div class="h-10 w-10 animate-spin rounded-full border-b-2 border-indigo-600"></div>
			</div>
		{:else if error}
			<div class="rounded-lg bg-red-50 p-6 text-center">
				<p class="text-red-700">{error}</p>
				<button
					class="mt-4 rounded bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
					on:click={goBack}
				>
					업데이트 목록으로 돌아가기
				</button>
			</div>
		{:else if updateItem}
			<div class="overflow-hidden rounded-lg bg-white shadow">
				<div class="px-4 py-5 sm:p-6">
					<div class="prose prose-sm sm:prose-base md:prose-lg prose-indigo max-w-none break-words">
						{@html marked(updateItem.content)}
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
