<script lang="ts">
	import { marked } from 'marked';
	import type { UpdateMetadata } from '$lib/updates';
	import { updateTypeInfo } from '$lib/updates';

	export let data;

	$: updates = data.updates || [];

	let currentPage = 1;
	let itemsPerPage = 5;
	$: totalPages = Math.ceil(updates.length / itemsPerPage);

	let selectedUpdate: UpdateMetadata | null = null;
	let showModal = false;

	$: paginatedUpdates = updates.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages) {
			currentPage = page;
		}
	}

	function openUpdateDetail(update: UpdateMetadata) {
		selectedUpdate = update;
		showModal = true;
	}

	function closeModal() {
		showModal = false;
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('ko-KR', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>업데이트 내역 - GarminFitBot</title>
</svelte:head>

<div class="py-12">
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="text-center">
			<h1 class="text-4xl font-bold text-gray-900">업데이트 내역</h1>
			<p class="mt-4 text-lg text-gray-500">GarminFitBot의 새로운 기능과 개선사항을 확인하세요.</p>
		</div>

		<div class="mt-12 space-y-6">
			{#each paginatedUpdates as update (update.id)}
				<div
					class="overflow-hidden rounded-lg border border-gray-200 bg-white shadow transition-shadow hover:shadow-md"
				>
					<div class="px-6 py-4">
						<div class="flex items-center justify-between">
							<div class="w-full">
								<button
									class="w-full text-left"
									on:click={() => openUpdateDetail(update)}
									aria-label={`${update.title} 상세 보기`}
								>
									<h2 class="break-words text-xl font-semibold text-gray-900 hover:text-indigo-600">
										{update.title}
									</h2>
								</button>
								<div class="mt-1 flex flex-wrap items-center gap-2 text-sm text-gray-500">
									<span
										class={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${updateTypeInfo[update.type].color}`}
									>
										{updateTypeInfo[update.type].icon}
										{updateTypeInfo[update.type].label}
									</span>
									<span>{formatDate(update.date)}</span>
								</div>
							</div>
						</div>
						<p class="mt-4 break-words text-gray-600">{update.summary}</p>
						<div class="mt-4 flex justify-end"></div>
					</div>
				</div>
			{/each}

			{#if updates.length === 0}
				<div class="rounded-lg bg-gray-50 p-6 text-center">
					<p class="text-gray-500">업데이트 내역이 없습니다.</p>
				</div>
			{/if}
		</div>

		<!-- 페이지네이션 -->
		{#if totalPages > 1}
			<div class="mt-8 flex justify-center">
				<nav class="flex items-center space-x-2" aria-label="Pagination">
					<button
						class="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
						on:click={() => goToPage(currentPage - 1)}
						disabled={currentPage === 1}
					>
						이전
					</button>
					{#each Array(totalPages) as _, i}
						<button
							class={`rounded-md px-3 py-2 text-sm font-medium ${
								currentPage === i + 1
									? 'bg-indigo-600 text-white'
									: 'border border-gray-300 bg-white text-gray-500 hover:bg-gray-50'
							}`}
							on:click={() => goToPage(i + 1)}
						>
							{i + 1}
						</button>
					{/each}
					<button
						class="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
						on:click={() => goToPage(currentPage + 1)}
						disabled={currentPage === totalPages}
					>
						다음
					</button>
				</nav>
			</div>
		{/if}
	</div>
</div>

<!-- 업데이트 상세 모달 -->
{#if showModal && selectedUpdate}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
		<div
			class="scrollbar-hide max-h-[90vh] w-full max-w-4xl overflow-y-auto scroll-smooth rounded-lg bg-white p-4 shadow-xl sm:p-6"
		>
			<div class="mb-4 flex flex-col justify-between sm:flex-row sm:items-center">
				<div class="mb-2 flex flex-col gap-2 sm:mb-0 sm:flex-row sm:items-center">
					<div class="flex flex-wrap gap-2">
						<span
							class={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${updateTypeInfo[selectedUpdate.type].color}`}
						>
							{updateTypeInfo[selectedUpdate.type].icon}
							{updateTypeInfo[selectedUpdate.type].label}
						</span>
						<span class="text-sm text-gray-500">{formatDate(selectedUpdate.date)}</span>
					</div>
				</div>
				<button class="text-gray-500 hover:text-gray-700" on:click={closeModal} aria-label="닫기">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
			<div class="prose prose-sm md:prose-base max-w-none break-words">
				{@html marked(selectedUpdate.content)}
			</div>
		</div>
	</div>
{/if}

<style>
	/* 스크롤바 숨기기 */
	.scrollbar-hide {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
	.scrollbar-hide::-webkit-scrollbar {
		display: none; /* Chrome, Safari, Opera */
	}
</style>
