<script lang="ts">
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>에러 - GarminFitBot</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full text-center space-y-8">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
				{$page.status === 404 ? '페이지를 찾을 수 없습니다' : '오류가 발생했습니다'}
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				{$page.error?.message || '잠시 후 다시 시도해주세요.'}
			</p>
		</div>
		<div class="mt-4">
			<svg class="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path 
					stroke-linecap="round" 
					stroke-linejoin="round" 
					stroke-width="2" 
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
		</div>
	</div>
</div>

<style>
	/* 추가적인 스타일링이 필요한 경우 여기에 작성 */
</style> 