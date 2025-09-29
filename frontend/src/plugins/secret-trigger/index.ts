import { type App } from 'vue'
import { initEasterEgg, type EasterEggOptions } from './easter-egg'
import EasterEgg from './components/EasterEgg.vue'

type SecretTriggerOptions = {
	easterEgg: EasterEggOptions
}

export const createSecretTrigger = (options: SecretTriggerOptions) => {
	return {
		install: (app: App) => {
			initEasterEgg(app, options.easterEgg)
			app.component('st-easter-egg', EasterEgg)
		}
	}
}

export { useEasterEgg } from './easter-egg'
