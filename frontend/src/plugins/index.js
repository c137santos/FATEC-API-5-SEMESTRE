/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import { loadFonts } from "./webfontloader"
import vuetify from "./vuetify"
import { createPinia } from "pinia"
import router from "../router"

import { createSecretTrigger } from './secret-trigger/index'

const secretTrigger = createSecretTrigger({
  easterEgg: {
		triggerMap: {
			konami: [
				'ArrowUp',
				'ArrowUp',
				'ArrowDown',
				'ArrowDown',
				'ArrowLeft',
				'ArrowRight',
				'ArrowLeft',
				'ArrowRight',
				'B',
				'A',
				'Enter'
			]
		}
	}
})

export function registerPlugins(app) {
  loadFonts()
  app.use(secretTrigger)
  app.use(vuetify).use(createPinia()).use(router)
}
