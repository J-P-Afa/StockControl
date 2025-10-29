import { ref } from 'vue'

// Estado global do menu
const isExpanded = ref(false)

export function useSideMenu() {
  const toggleExpansion = () => {
    isExpanded.value = !isExpanded.value
  }

  const expand = () => {
    isExpanded.value = true
  }

  const collapse = () => {
    isExpanded.value = false
  }

  return {
    isExpanded,
    toggleExpansion,
    expand,
    collapse
  }
}
