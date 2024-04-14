<template>
  <div>
    <h1>포트폴리오</h1>
    <div class="portfolio-meter-group">
      <MeterGroup :value="meterValues" labelPosition="end" labelOrientation="horizontal" />
    </div>
    <Panel v-if="portfolio">
      <TreeTable :value="treeTableData">
        <Column class="w-5" field="name" header="이름" expander></Column>
        <Column field="percentage" header="비중"></Column>
        <Column field="total_value" header="가치"></Column>
        <Column field="rtn" header="수익률"></Column>
        <template #footer>
          <div class="right-0">
            <span>{{ toCurrency(portfolio.total_value) }}</span>
          </div>
        </template>
      </TreeTable>
    </Panel>
  </div>
</template>


<script setup>
import { computed, onMounted, ref } from 'vue';
import axios from 'axios';
import TreeTable from 'primevue/treetable';
import MeterGroup from 'primevue/metergroup';
import Panel from 'primevue/panel';
import Column from 'primevue/column';
import { toCurrency, toPercentage } from './utils';

const portfolio = ref(null);

onMounted(async () => {
  portfolio.value = await fetchPortfolioData();
});

const groupedAssets = computed(() => {
  if (!portfolio.value) return [];
  // portfolio 데이터를 변환하고 자산군별로 그룹화합니다.
  const data = transformPortfolioData(portfolio.value);
  let assetGroups = groupAssetsByClass(data.positions, data.total_value);
  // 그룹화된 자산군을 비중에 따라 정렬합니다.
  return sortAssetGroups(assetGroups);
});

const treeTableData = computed(() => {
  return groupedAssets.value.map((group, index) => ({
    key: `group-${index}`,
    data: {
      name: translateAssetClassName(group.name),
      percentage: toPercentage(group.percentage),
      total_value: toCurrency(group.total_value),
      rtn: toPercentage(group.average_rtn)
    },
    children: group.positions.map((position, childIndex) => ({
      key: `position-${index}-${childIndex}`,
      data: {
        name: position.asset.label,
        percentage: toPercentage(calcWeight(position.total_amount, portfolio.value.total_value)),
        total_value: toCurrency(position.total_amount),
        rtn: toPercentage(position.rtn)
      }
    }))
  }));
});

const meterValues = computed(() => {
  return groupedAssets.value.map(group => ({
    label: translateAssetClassName(group.name),
    color: getColorForAssetClass(group.name),
    value: group.percentage * 100 // Convert to a 0-100 scale for MeterGroup
  }));
});

function calcWeight(value, total) {
  return value / total;
}

function transformPortfolioData(data) {
  // API 응답에서 positions 배열 복사
  const positionsCopy = [...data.positions];

  // 현금 잔액을 positions 배열에 추가
  positionsCopy.push({
    asset: {
      label: '현금',
      symbol: 'CASH',
      asset_class: 'CASH'
    },
    quantity: '-',
    sellable_quantity: '-',
    average_buy_price: '-',
    total_amount: data.cash_balance,
    rtn: 0
  });

  return {
    ...data,
    positions: positionsCopy
  };
}

function groupAssetsByClass(positions, totalValue) {
  // 자산군별로 그룹화된 객체를 생성합니다.
  const assetGroups = {};

  positions.forEach(position => {
    const assetClass = position.asset.asset_class;
    if (!assetGroups[assetClass]) {
      // 자산군별로 초기 객체를 생성합니다.
      assetGroups[assetClass] = {
        name: assetClass,
        total_value: 0,
        positions: [],
        average_rtn: 0,
        total_rtn: 0
      };
    }

    // 자산군에 포지션을 추가하고, 가치와 수익률을 누적합니다.
    assetGroups[assetClass].positions.push(position);
    assetGroups[assetClass].total_value += position.total_amount;
    assetGroups[assetClass].total_rtn += position.total_amount * position.rtn;
  });

  // 각 자산군의 비중과 평균 수익률을 계산합니다.
  Object.values(assetGroups).forEach(group => {
    group.percentage = group.total_value / totalValue;
    group.average_rtn = group.total_value > 0 ? (group.total_rtn / group.total_value) : 0;
  });

  return Object.values(assetGroups); // 배열로 변환하여 반환합니다.
}

function sortAssetGroups(assetGroups) {
  // 자산군을 비중에 따라 정렬합니다.
  assetGroups.sort((a, b) => b.percentage - a.percentage);

  // 각 자산군 내의 자산들을 비중에 따라 정렬합니다.
  assetGroups.forEach(group => {
    group.positions.sort((a, b) => b.percentage - a.percentage);
  });

  return assetGroups;
}

async function fetchPortfolioData() {
  try {
    const response = await axios.get('http://localhost:8000/portfolio');
    return response.data;
  } catch (error) {
    console.error("포트폴리오 데이터를 가져오는데 실패했습니다.", error);
    return null; // 오류 발생 시 null 반환
  }
}

function translateAssetClassName(className) {
  const nameMap = {
    "STOCK": "주식",
    "BOND": "채권",
    "CASH": "현금성 자산",
    "COMMODITY": "원자재",
    "OTHER": "기타"
  };

  return nameMap[className] || className;
}

function getColorForAssetClass(assetClass) {
  const colors = {
    STOCK: '#3498db',
    BOND: '#9b59b6',
    CASH: '#2ecc71',
    COMMODITY: '#f1c40f',
    OTHER: '#e74c3c'
  };
  return colors[assetClass] || '#bdc3c7'; // 기본 색상 설정
}

</script>

<style>
.p-panel {
  padding: 0.5rem 0;
}

.p-panel-header {
  padding-top: 0;
}

.portfolio-meter-group {
  /* margin-top: 0.5rem; */
  margin-bottom: 2rem;
}
</style>