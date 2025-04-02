<script lang="ts">
	import chatbotCollectFitData from '$lib/images/screenshots/chatbot-collect-fit-data.png';
	import resultCollectFitData from '$lib/images/screenshots/result-collect-fit-data.png';
	import chatbotAnalysisHealth from '$lib/images/screenshots/chatbot-analysis-health.png';
	import resultAnalysisHealth from '$lib/images/screenshots/result-analysis-health.png';

	const kakaoChannel = {
		name: '카카오톡 챗봇',
		description: 'GarminFitBot 카카오톡 채널을 추가하여 건강 데이터 분석 서비스를 이용해보세요.',
		link: 'https://pf.kakao.com/_GVxmnn',
		icon: '💬'
	};

	const steps = [
		{
			title: '카카오톡 채널 추가',
			description: 'GarminFitBot 카카오톡 채널을 추가합니다.',
			icon: '📱'
		},
		{
			title: 'Garmin Connect 계정 연동',
			description: '카카오톡 챗봇에서 Garmin Connect 계정을 연동합니다.',
			icon: '🔗'
		},
		{
			title: '데이터 수집 요청',
			description: '챗봇에 "데이터 수집해줘"라고 입력하여 건강 데이터를 수집합니다.',
			icon: '📊'
		},
		{
			title: 'AI 분석 요청',
			description: '챗봇에 건강 관련 질문을 입력하여 AI의 분석 결과를 받아봅니다.',
			icon: '🤖'
		}
	];

	const screenshots = [
		{
			title: '데이터 수집',
			description: '챗봇에 "데이터 수집해줘"라고 입력하면 Garmin 기기의 건강 데이터를 수집합니다.',
			images: [
				{
					src: chatbotCollectFitData,
					alt: '데이터 수집 요청'
				},
				{
					src: resultCollectFitData,
					alt: '데이터 수집 결과'
				}
			]
		},
		{
			title: 'AI 분석',
			description: '수집된 데이터를 바탕으로 AI가 건강 상태를 분석하고 리포트를 제공합니다.',
			images: [
				{
					src: chatbotAnalysisHealth,
					alt: 'AI 분석 요청'
				},
				{
					src: resultAnalysisHealth,
					alt: 'AI 분석 결과'
				}
			]
		}
	];
</script>

<svelte:head>
	<title>GarminFitBot</title>
</svelte:head>

<div class="py-12">
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="text-center">
			<h1 class="text-4xl font-bold text-gray-900">GarminFitBot</h1>
			<p class="mt-4 text-lg text-gray-500">
				Garmin 기기의 건강 데이터를 AI로 분석하여 더 나은 건강 관리를 도와드립니다.
			</p>
			<p class="text-center text-lg text-gray-500">
				GarminFitBot 카카오톡 채널을 추가하고 건강 데이터 분석을 시작해보세요.
			</p>

		</div>

		<!-- 데모 -->
		<div class="mt-16">
			<h2 class="text-center text-2xl font-bold text-gray-900">이렇게 작동합니다</h2>
			<p class="mt-4 text-center text-lg text-gray-500">GarminFitBot의 주요 기능을 살펴보세요.</p>

			<div class="mt-12 space-y-16">
				{#each screenshots as screenshot}
					<div
						class="relative rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
					>
						<h3 class="mb-6 text-center text-xl font-semibold text-gray-900">{screenshot.title}</h3>
						<p class="mb-8 text-center text-gray-500">{screenshot.description}</p>

						<div class="grid gap-4 sm:grid-cols-2">
							{#each screenshot.images as image}
								<div class="relative h-[400px]">
									<img
										src={image.src}
										alt={image.alt}
										class="absolute inset-0 h-full w-full rounded-lg object-contain shadow-md"
									/>
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- 사용방법 -->
		<div class="mt-16">
			<h2 class="text-center text-2xl font-bold text-gray-900">사용방법</h2>
			<p class="mt-4 text-center text-lg text-gray-500">
				GarminFitBot을 시작하는 방법을 안내해드립니다.
			</p>

			<div class="mt-12">
				<div class="flow-root">
					<ul role="list" class="-mb-8">
						{#each steps as step, i}
							<li>
								<div class="relative pb-8">
									{#if i !== steps.length - 1}
										<span
											class="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
											aria-hidden="true"
										></span>
									{/if}
									<div class="relative flex space-x-3">
										<div>
											<span
												class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-white"
											>
												{step.icon}
											</span>
										</div>
										<div class="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
											<div>
												<p class="mt-1 text-sm font-medium text-gray-900">
													{step.title}
												</p>
												<p class="text-sm text-gray-500">
													{step.description}
												</p>
											</div>
										</div>
									</div>
								</div>
							</li>
						{/each}
					</ul>
				</div>
			</div>

			<div class="mt-8 flex justify-center">
				<a
					href={kakaoChannel.link}
					target="_blank"
					rel="noopener noreferrer"
					class="kakao-button inline-flex items-center rounded-lg bg-yellow-400 px-6 py-3 text-lg font-semibold text-black shadow-sm hover:bg-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2"
				>
					<span class="mr-2 text-2xl">{kakaoChannel.icon}</span>
					카카오톡 채널 추가하기
				</a>
			</div>
		</div>
	</div>
</div>
