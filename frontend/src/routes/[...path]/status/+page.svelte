<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/state';
	import { PUBLIC_API_URL } from '$env/static/public';
	import type { TaskName, TaskDisplayInfo, CollectorResult, TaskResult } from '$lib/type';
	import { marked } from 'marked';

	export let data;

	marked.setOptions({
		breaks: true,
		gfm: true
	});

	let status = data.status;
	let intervalId: number;
	let showModal = false;
	let mdResult = '';

	$: taskParts = page.params.path.split('/');
	$: userKey = taskParts[0];
	$: date = taskParts[1];
	$: taskName = taskParts[2];

	const taskDisplayInfo: Record<TaskName, TaskDisplayInfo> = {
		'collect-fit-data': {
			title: '데이터 수집',
			description: '가민 핏 데이터를 수집합니다.',
			resultTitle: '수집 결과',
			collectorMapping: {
				HeartRateCollector: '심박수 데이터',
				StressCollector: '스트레스 데이터',
				StepsCollector: '활동량 데이터',
				SleepCollector: '수면 데이터',
				ActivityCollector: '운동 데이터'
			}
		},
		'analysis-health': {
			title: 'AI 분석',
			description: 'AI가 건강 데이터를 분석하고 있습니다.',
			resultTitle: '분석 결과'
		}
	};

	const defaultTaskInfo: TaskDisplayInfo = {
		title: '작업 실행',
		description: '요청하신 작업을 실행하고 있습니다.',
		resultTitle: '실행 결과'
	};

	$: currentTask = (taskName && taskDisplayInfo[taskName as TaskName]) || defaultTaskInfo;

	$: statusInfo = {
		PENDING: {
			message: '작업이 존재하지 않습니다...',
			color: 'text-gray-500'
		},
		PROGRESS: {
			message: '작업이 진행 중입니다...',
			color: 'text-yellow-500'
		},
		STARTED: {
			message: '작업이 진행 중입니다...',
			color: 'text-blue-500'
		},
		SUCCESS: {
			message: '작업이 완료되었습니다!',
			color: 'text-green-500'
		},
		FAILURE: {
			message: '작업 실행 중 오류가 발생했습니다.',
			color: 'text-red-500'
		}
	}[status.status];

	function formatResult(result: TaskResult): CollectorResult[] {
		if (taskName === 'collect-fit-data' && typeof result === 'object') {
			const collectors = Object.keys(currentTask.collectorMapping || {});
			return collectors.map((collector) => ({
				name: (currentTask.collectorMapping?.[collector] ?? collector) as string,
				status: result[collector]?.includes('성공')
					? '성공'
					: result[collector]?.includes('실패')
						? '실패'
						: '없음'
			}));
		}
		return [];
	}

	function openModal(result: string) {
		mdResult = result;
		showModal = true;
	}

	function closeModal() {
		showModal = false;
	}

	onMount(() => {
		if (['STARTED', 'PROGRESS'].includes(status.status)) {
			intervalId = setInterval(async () => {
				try {
					const response = await fetch(`${PUBLIC_API_URL}/task/${data.task_id}/status`);
					const result = await response.json();
					status = result.data;

					if (['SUCCESS', 'FAILURE'].includes(result.data.status)) {
						clearInterval(intervalId);
					}
				} catch (error) {
					console.error('상태 확인 중 오류:', error);
				}
			}, 3000);
		}
	});

	onDestroy(() => {
		if (intervalId) clearInterval(intervalId);
	});
</script>

<svelte:head>
	<title>{currentTask.title} - GarminFitBot</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
	<div class="w-full max-w-md space-y-8">
		<div class="text-center">
			<h1 class="text-3xl font-bold">{currentTask.title}</h1>
			<p class="mt-2 text-gray-400">
				{date}
				{currentTask.description}
			</p>
		</div>

		<div class="mt-8 rounded-lg bg-white p-6 shadow">
			<div class="text-center">
				<div class={`text-xl font-semibold ${statusInfo.color}`}>
					{statusInfo.message}
				</div>

				{#if status.status === 'SUCCESS' && status.result}
					<div class="mt-4 rounded-md bg-green-50 p-4">
						<h3 class="text-lg font-medium text-green-800">{currentTask.resultTitle}</h3>

						{#if taskName === 'collect-fit-data'}
							<div class="mt-4">
								<table class="min-w-full">
									<thead>
										<tr class="border-b">
											<th class="py-2">데이터 종류</th>
											<th class="py-2">상태</th>
										</tr>
									</thead>
									<tbody>
										{#each formatResult(status.result) as item}
											<tr class="border-b">
												<td class="py-2">{item.name}</td>
												<td class="py-2">
													<span
														class={item.status === '성공'
															? 'text-green-600'
															: item.status === '실패'
																? 'text-red-600'
																: 'text-gray-600'}
													>
														{item.status}
													</span>
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						{:else if taskName === 'analysis-health' && typeof status.result === 'string'}
							<div class="mt-4">
								<div class="max-h-60 overflow-y-auto whitespace-pre-wrap text-sm text-green-700">
									{status.result?.substring(0, 250)}...
								</div>
								<button
									class="mt-4 rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
									on:click={() => typeof status.result === 'string' && openModal(status.result)}
								>
									전체 분석 결과 보기
								</button>
							</div>
						{:else}
							<pre class="mt-2 whitespace-pre-wrap text-sm text-green-700">
                {JSON.stringify(status.result, null, 2)}
              </pre>
						{/if}
					</div>
				{/if}

				{#if status.status === 'FAILURE' && status.error}
					<div class="mt-4 rounded-md bg-red-50 p-4">
						<h3 class="text-lg font-medium text-red-800">오류 내용</h3>
						<p class="mt-2 text-sm text-red-700">
							{JSON.stringify(status.error, null, 2)}
						</p>
					</div>
				{/if}

				{#if ['STARTED', 'PROGRESS'].includes(status.status)}
					<div class="mt-4">
						<div class="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-gray-900"></div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

{#if showModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
		<div
			class="scrollbar-hide max-h-[90vh] w-full max-w-4xl overflow-y-auto scroll-smooth rounded-lg bg-white p-6 shadow-xl"
		>
			<div class="mb-4 flex items-center justify-end">
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
			<div class="prose prose-sm md:prose-base max-w-none">
				{@html marked(mdResult)}
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
