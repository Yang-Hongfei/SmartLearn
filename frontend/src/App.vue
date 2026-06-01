<script setup>
import gsap from 'gsap'

function onEnter(el, done) {
  gsap.fromTo(el, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.25, ease: 'power2.out', onComplete: done })
}

function onLeave(el, done) {
  gsap.to(el, { opacity: 0, y: -6, duration: 0.18, ease: 'power2.in', onComplete: done })
}
</script>

<template>
  <router-view v-slot="{ Component }">
    <transition mode="out-in" @enter="onEnter" @leave="onLeave" appear>
      <component :is="Component" />
    </transition>
  </router-view>
</template>
