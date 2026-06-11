<template>
  <div class="app-header">
    <div class="header-left">
      <h1 class="logo" @click="router.push('/dashboard')">省队青训营训练档案平台</h1>
      <el-menu
        v-if="authStore.isCoach"
        mode="horizontal"
        :default-active="activeMenu"
        class="nav-menu"
        router
      >
        <el-menu-item index="/students">学员管理</el-menu-item>
        <el-menu-item index="/training">训练录入</el-menu-item>
        <el-menu-item index="/assessments">体测录入</el-menu-item>
        <el-menu-item index="/comments">教练评语</el-menu-item>
        <el-menu-item index="/promotions">晋升管理</el-menu-item>
      </el-menu>
      <el-menu
        v-else-if="authStore.isParent"
        mode="horizontal"
        :default-active="activeMenu"
        class="nav-menu"
        router
      >
        <el-menu-item :index="`/students/${authStore.user?.student_id}`">我的孩子</el-menu-item>
        <el-menu-item index="/comments">教练评语</el-menu-item>
      </el-menu>
    </div>
    <div class="header-right">
      <span class="user-info">
        <el-tag :type="authStore.isCoach ? 'primary' : 'success'" size="small">
          {{ authStore.isCoach ? '教练' : '家长' }}
        </el-tag>
        {{ authStore.user?.username || '' }}
      </span>
      <el-button type="danger" text @click="handleLogout">退出登录</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

function handleLogout() {
  authStore.logout()
}
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 18px;
  color: #409eff;
  margin-right: 32px;
  cursor: pointer;
  white-space: nowrap;
}

.nav-menu {
  border-bottom: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}
</style>
