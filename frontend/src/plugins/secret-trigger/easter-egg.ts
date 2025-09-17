import { inject, ref, type App } from 'vue'
import config from './config'

const createEasterEgg = (codeName: string, code: string[]) => ({
	name: codeName,
	code: code.map((c) => c.toUpperCase()),
	active: false,
	nextInputIndex: 0
})

const INJECT_KEY = `${config.PLUGIN_INJECT_KEY}:${config.EASTER_EGG_INJECT_KEY}`

type EasterEgg = ReturnType<typeof createEasterEgg>

const triggerNextStep = (event: KeyboardEvent, easterEgg: EasterEgg) => {
	easterEgg = Object.assign({}, easterEgg)
	const expectedValue = easterEgg.code[easterEgg.nextInputIndex]
	if (expectedValue !== event.key.toUpperCase()) {
		easterEgg.nextInputIndex = 0
		return easterEgg
	}

	easterEgg.nextInputIndex++

	if (easterEgg.code.length === easterEgg.nextInputIndex) {
		easterEgg.nextInputIndex = 0
		easterEgg.active = !easterEgg.active
	}
	return easterEgg
}

type TriggerMap = Record<string, string[]>
const craeteStateList = (triggerMap: TriggerMap) => {
	const easterEggList = ref(Object.entries(triggerMap).map((entry) => ref(createEasterEgg(...entry))))

	document.addEventListener('keydown', (event) => {
		for (const easterEgg of easterEggList.value) {
			const updatedEasterEgg = triggerNextStep(event, easterEgg.value)
			Object.assign(easterEgg.value, updatedEasterEgg)
		}
	})

	return easterEggList
}
type EasterEggStateList = ReturnType<typeof craeteStateList>

export type EasterEggOptions = {
	triggerMap: TriggerMap
}

export const useEasterEgg = (code: string) => {
	const stateList = inject<EasterEggStateList>(INJECT_KEY)
	const state = stateList?.value.find((state) => state.value.name === code)
	if (!state) {
		throw new Error(`[secret-trigger]: No code with name ${code}`)
	}
	return state
}

export const initEasterEgg = (app: App, options: EasterEggOptions) => {
	const stateList = craeteStateList(options.triggerMap)
	app.provide<EasterEggStateList>(INJECT_KEY, stateList)
}
