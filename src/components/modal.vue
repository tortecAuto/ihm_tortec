<template>
    <div class="tooltip" v-if="isVisible" :style="{ left: x + 'px', top: y + 'px' }">
      <button @click="closeModal">X</button>
      <p>Informação: - Valor atual: {{ currentValue }}°C</p>
      <button @click="decrement">-</button>
      <input type="number" v-model="currentValue" @change="logValue">
      <button @click="increment">+</button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      initialPosition: {
        type: Object,
        required: true
      },
      initialValue: {
        type: Number,
        required: true
      }
    },
    data() {
      return {
        currentValue: this.initialValue,
        isVisible: true,
        x: 0,
        y: 0
      };
    },
    mounted() {
      this.setPosition();
    },
    methods: {
      closeModal() {
        this.isVisible = false;
      },
      increment() {
        this.currentValue++;
      },
      decrement() {
        this.currentValue--;
      },
      logValue() {
        console.log(`Novo valor: ${this.currentValue}°C`);
      },
      setPosition() {
        const { x, y, width, height } = this.initialPosition;
        this.x = x + width / 2;
        this.y = y + height / 2;
      }
    }
  }
  </script>
  
  <style scoped>
  .tooltip {
    position: absolute;
    background-color: white;
    border: 1px solid black;
    padding: 10px;
  }
  </style>
  