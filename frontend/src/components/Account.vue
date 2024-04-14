<template>
  <div class="container">
    <form @submit.prevent="submitAccount">
      <div class="container">
        <label for="brokerage" class="label">증권사</label>
        <Dropdown id="brokerage" v-model="accountData.brokerage" :options="brokerages" optionLabel="name"
          optionValue="value" placeholder="증권사를 선택해주세요." />
      </div>
      <div class="container">
        <label for="appKey" class="label">APP_KEY</label>
        <InputText id="appKey" v-model="accountData.app_key" type="password" required />
      </div>
      <div class="container">
        <label for="secretKey" class="label">SECRET_KEY</label>
        <InputText id="secretKey" v-model="accountData.secret_key" type="password" required />
      </div>
      <div class="button-container p-fluid">
        <Button type="submit" label="계좌 등록하기" />
      </div>
      <p v-if="accountSubmissionResultMessage">{{ accountSubmissionResultMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';
import InputText from 'primevue/inputtext'; // Import for input fields
import Dropdown from 'primevue/dropdown'; // Import for select
import Button from 'primevue/button'; // Import for buttons

const brokerages = [
  { name: '이베스트', value: 'ebest' },
  { name: '한국투자증권', value: 'korea_investment' },
];

const accountData = reactive({
  brokerage: null,
  app_key: '',
  secret_key: '',
});

const accountSubmissionResultMessage = ref('');

async function submitAccount() {
  try {
    const response = await axios.post('http://localhost:8000/accounts', accountData);
    console.log(response.data); // 성공 응답 처리
    accountSubmissionResultMessage.value = '계좌가 성공적으로 등록되었습니다.';
  } catch (error) {
    console.error('계좌 등록에 실패했습니다:', error);
    accountSubmissionResultMessage.value = '계좌 등록에 실패했습니다.';
  }
}

</script>

<style scoped>
.container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.label {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-right: 1rem;

}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.p-dropdown {
  width: 68%;
}
</style>
