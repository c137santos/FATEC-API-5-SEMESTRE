<template>
	<v-sheet 
		class="mx-auto my-8 bg-transparent"
		max-width="1400"
	>
		<st-easter-egg code="konami">
			<div style="position: fixed; z-index: 1000; left: -8px; top: 50px">
				<slot name="easter-egg" />
			</div>
		</st-easter-egg>
		<v-container>
			<v-row>
				<v-col>
					<h2>
						<slot name="title" />
					</h2>
				</v-col>
		 	</v-row>
			<slot></slot>
		</v-container>
	</v-sheet>
</template>