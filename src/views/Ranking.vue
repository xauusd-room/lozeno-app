
<template>
  <main class="ranking-page page-container">
    <RankingHero />
    <RankingList />
  </main>
</template>

<script setup>
import RankingHero from '../components/RankingHero.vue'
import RankingList from '../components/RankingList.vue'
</script>

<style scoped>
.ranking-page{min-width:0;padding-top:32px;padding-bottom:32px}
</style>
