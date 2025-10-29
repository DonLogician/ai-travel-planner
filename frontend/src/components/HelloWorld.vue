<script setup>
import { ref } from 'vue'

defineProps({
  msg: String,
})

const count = ref(0)
</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">当前计数：{{ count }}</button>
    <p>
      编辑
      <code>components/HelloWorld.vue</code>
      体验热更新效果
    </p>
  </div>

  <p>
    查看
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank">
      create-vue 官方脚手架
    </a>
    获取更多入门指南
  </p>
  <p>
    了解更多关于 Vue 在 IDE 中的支持，请阅读
    <a
      href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support"
      target="_blank"
    >
      官方工具链文档
    </a>
    。
  </p>
  <p class="read-the-docs">点击 Vite 与 Vue 图标获取更多信息</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
