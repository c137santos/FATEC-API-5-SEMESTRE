<template>
	<component :is="tag ?? 'div'" v-if="easterEgg.active">
		<slot></slot>
	</component>
</template>

<script setup lang="ts">
import { useEasterEgg } from '..'

type Props = {
	tag?: string
	code: string
}
const { tag, code } = defineProps<Props>()

const easterEgg = useEasterEgg(code)

</script>
