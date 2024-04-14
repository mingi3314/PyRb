// 숫자를 통화 형식으로 변환
export function toCurrency(value) {
    return value.toLocaleString('ko-KR', { style: 'currency', currency: 'KRW' });
}


export function toPercentage(value) {
    return `${(value * 100).toFixed(2)}%`;
}