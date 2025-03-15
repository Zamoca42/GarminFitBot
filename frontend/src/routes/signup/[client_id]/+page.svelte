<script lang="ts">
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { goto } from '$app/navigation';

	interface ErrorWithMessage {
    message: string;
  }

	let garminId = '';
	let password = '';
	let errorMessage = '';
	let showToast = false;
	let loginAttempts = 0;
	let isLoading = false;
	let isSuccess = false;

	$: clientId = page.params.client_id;
	$: isLocked = loginAttempts >= 5;

	function isErrorWithMessage(error: unknown): error is ErrorWithMessage {
    return (
      typeof error === 'object' &&
      error !== null &&
      'message' in error &&
      typeof (error as Record<string, unknown>).message === 'string'
    );
  }

  function getErrorMessage(error: unknown): string {
    if (isErrorWithMessage(error)) {
      return error.message;
    }
    return '알 수 없는 오류가 발생했습니다.';
  }

	async function handleSubmit() {
		if (isLocked) {
			showError('로그인이 제한되었습니다. 잠시 후 다시 시도해주세요.');
			return;
		}

		if (!garminId || !password) {
			showError('Garmin ID와 비밀번호를 입력해주세요.');
			return;
		}

		isLoading = true;
		
		try {
			const response = await fetch(`${PUBLIC_API_URL}/auth/signup`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					garmin_id: garminId,
					password: password,
					client_id: clientId
				})
			});

			const data = await response.json();

			if (!response.ok) {
				loginAttempts++;
				throw new Error(data.message || '로그인에 실패했습니다.');
			}

			isSuccess = true;
			goto(`/signup/complete`);

		} catch (error: unknown) {
			showError(getErrorMessage(error));
			resetForm();
		} finally {
			isLoading = false;
		}
	}

	function showError(message: string) {
		errorMessage = message;
		showToast = true;
		setTimeout(() => {
			showToast = false;
			errorMessage = '';
		}, 3000);
	}

	function resetForm() {
		garminId = '';
		password = '';
	}
</script>

<svelte:head>
	<title>회원가입 - GarminFitBot</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
				GarminFitBot 회원가입
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Garmin Connect 계정으로 등록하세요
			</p>
		</div>
		<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="rounded-md shadow-sm -space-y-px">
				<div>
					<label for="garmin-id" class="sr-only">Garmin ID</label>
					<input
						id="garmin-id"
						name="garmin-id"
						type="email"
						required
						class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
						placeholder="Garmin ID"
						bind:value={garminId}
						disabled={isLocked || isLoading}
					/>
				</div>
				<div>
					<label for="password" class="sr-only">비밀번호</label>
					<input
						id="password"
						name="password"
						type="password"
						required
						class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
						placeholder="비밀번호"
						bind:value={password}
						disabled={isLocked || isLoading}
					/>
				</div>
			</div>

			<div>
				<button
					type="submit"
					class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
					disabled={isLocked || isLoading}
				>
					{#if isLoading}
						<span class="absolute left-0 inset-y-0 flex items-center pl-3">
							<!-- Loading spinner -->
							<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
						</span>
						처리중...
					{:else}
						회원가입
					{/if}
				</button>
			</div>
		</form>
	</div>
</div>

{#if showToast && !isSuccess}
	<div
		transition:fade
		class="fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg bg-red-500 text-white"
	>
		{errorMessage}
	</div>
{/if}

<style>
	/* 추가적인 스타일링이 필요한 경우 여기에 작성 */
</style> 