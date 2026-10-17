import { ref, onMounted, onBeforeUnmount, type Ref, markRaw } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsCoreOption } from 'echarts'

export function useECharts(elRef: Ref<HTMLElement | null>) {
  const chartInstance = ref<ECharts | null>(null)
  let resizeObserver: ResizeObserver | null = null

  const initChart = () => {
    if (!elRef.value) return
    if (!chartInstance.value) {
      const chart = echarts.init(elRef.value)
      chartInstance.value = markRaw(chart)
    }
  }

  const setOption = (option: EChartsCoreOption, notMerge: boolean = false) => {
    if (!chartInstance.value) {
      initChart()
    }
    chartInstance.value?.setOption(option, notMerge)
  }

  const resize = () => {
    chartInstance.value?.resize()
  }

  const showLoading = () => {
    chartInstance.value?.showLoading({
      text: '数据加载中...',
      color: '#409EFF',
      textColor: '#333333',
      maskColor: 'rgba(255, 255, 255, 0.7)'
    })
  }

  const hideLoading = () => {
    chartInstance.value?.hideLoading()
  }

  const clear = () => {
    chartInstance.value?.clear()
  }

  onMounted(() => {
    initChart()
    if (elRef.value) {
      resizeObserver = new ResizeObserver(() => {
        resize()
      })
      resizeObserver.observe(elRef.value)
    }
    window.addEventListener('resize', resize)
  })

  onBeforeUnmount(() => {
    if (resizeObserver && elRef.value) {
      resizeObserver.unobserve(elRef.value)
      resizeObserver.disconnect()
      resizeObserver = null
    }
    window.removeEventListener('resize', resize)
    chartInstance.value?.dispose()
    chartInstance.value = null
  })

  return {
    chartInstance,
    setOption,
    resize,
    showLoading,
    hideLoading,
    clear
  }
}
