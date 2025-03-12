<script lang="ts">
	import { page } from '$app/stores';
	
	$: clientId = $page.url.searchParams.get('client_id');
</script>

<svelte:head>
	<title>회원가입 완료 - GarminFitBot</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full text-center space-y-8">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
				회원가입이 완료되었습니다!
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				카카오톡 챗봇으로 돌아가 서비스를 이용해주세요.
			</p>
		</div>
		<div class="mt-4">
			<svg class="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
			</svg>
		</div>
	</div>
</div> 