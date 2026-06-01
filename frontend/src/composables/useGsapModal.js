import { ref, watch, nextTick } from 'vue'
import gsap from 'gsap'

/**
 * Reusable GSAP modal animation composable.
 * Handles enter/leave lifecycle so v-if based modals can animate out
 * before being removed from the DOM.
 *
 * Usage:
 *   const { show, overlayRef, dialogRef } = useGsapModal(() => props.visible)
 *   // Use show (not visible) in your v-if
 *   // Bind overlayRef / dialogRef to template refs
 *
 * @param {import('vue').Ref<boolean>|Function} visibleSource - ref or getter returning visibility
 * @param {Object} [options]
 * @param {number} [options.duration=0.3] - animation duration in seconds
 * @param {boolean} [options.scale=true] - whether to use scale+opacity on dialog
 */
export function useGsapModal(visibleSource, options = {}) {
  const { duration = 0.3, scale = true } = options

  const show = ref(false)
  const overlayRef = ref(null)
  const dialogRef = ref(null)

  function animateIn() {
    const tl = gsap.timeline()
    tl.fromTo(overlayRef.value, { opacity: 0 }, { opacity: 1, duration: duration * 0.7 })
    if (dialogRef.value && scale) {
      tl.fromTo(
        dialogRef.value,
        { scale: 0.92, opacity: 0 },
        { scale: 1, opacity: 1, duration: duration, ease: 'back.out(1.7)' },
        '-=60%'
      )
    } else if (dialogRef.value) {
      tl.fromTo(dialogRef.value, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: duration }, '-=60%')
    }
  }

  function animateOut(onComplete) {
    const tl = gsap.timeline({ onComplete })
    if (dialogRef.value && scale) {
      tl.to(dialogRef.value, { scale: 0.95, opacity: 0, duration: duration * 0.6, ease: 'power2.in' })
    } else if (dialogRef.value) {
      tl.to(dialogRef.value, { opacity: 0, y: 8, duration: duration * 0.6, ease: 'power2.in' })
    }
    tl.to(overlayRef.value, { opacity: 0, duration: duration * 0.5 }, '-=40%')
  }

  const stopWatch = watch(
    visibleSource,
    async (val) => {
      if (val) {
        show.value = true
        await nextTick()
        animateIn()
      } else if (show.value) {
        animateOut(() => {
          show.value = false
        })
      }
    },
    { immediate: false }
  )

  return { show, overlayRef, dialogRef, stopWatch }
}
