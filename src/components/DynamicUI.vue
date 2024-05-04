<template>
  <div v-if="genericInputVisible" class="genericInput"
    :style="{ left: genericInputX + 'px', top: genericInputY + 'px', position: 'absolute' }">
    <h4>Alterar {{ genericInputLabel }}</h4>

    <div class="inputContainer">
      <input type="text" v-model="genericInput" class="big-input textCenter" />

    </div>

    <div class="arrowContainer">
      <img src="/img/up_arrow.png" class="arrow" @click="sumGenericInput">
      <img src="/img/down_arrow.png" class="arrow" @click="difGenericInput">
    </div>

    <div class="buttonContainer">
      <button class="btn-success" @click="saveGenericInput">
        <img src="/img/ok.png" alt="OK" class="buttonIcon">OK
      </button>
      <button class="btn-back" @click="genericInputVisible = false, setEdited(genericInputId)">
        <img src="/img/back.png" alt="Back" class="buttonIcon">Voltar
      </button>
    </div>
  </div>

  <div ref="placeholder" style="width: 100%; height: 800px;">

  </div>
  <div v-if="selectionBox.visible" class="selection-rectangle" :style="{left: selectionBox.x + 'px', top: selectionBox.y + 'px', width: selectionBox.width + 'px', height: selectionBox.height + 'px'}"></div>

</template>

<script>
import * as joint from 'jointjs';
import 'jointjs/dist/joint.css';

// import axios
import axios from 'axios';

export default {
  components: {

  },
  data() {
    return {
      selectedElements: [],
      selectionBox: {
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      visible: false
    },
    isSelecting: false,
      wait_com: false,
      wss: [], // Array para armazenar as instâncias WebSocket
      intervals: [],
      genericInputTag: '',
      genericInputId: null,
      genericInputX: 0,
      genericInputY: 0,
      genericInput: 0,
      genericInputVisible: false,
      genericInputLabel: '--',
      prog: [],
      draggable: false, // Controle de arrasto,
      graph: null,
      rangeValues: {},
      jsonCom: {
        ip: "192.168.0.202",
        data: {
          corrente_atual: 56,
          corrente_set: 50,
          temp_atual: 40,
          temp_set: 90,
          temp_rol: 45
        }
      }
    };
  },
  name: 'ScadaDiagram',
  methods: {
    selectElement(element) {
     // console.log(element.attributes.id);
  const elementId = element.attributes.id;
  const index = this.selectedElements.indexOf(elementId);
  if (index === -1) {
    this.selectedElements.push(elementId);
    element.attr('body/stroke', 'red'); // Marca como selecionado
  } else {
    this.selectedElements.splice(index, 1);
    element.attr('body/stroke', 'black'); // Marca como não selecionado
  }
},
    connect() {
      this.prog["com"].forEach((com, index_com) => {
      // Cria uma nova conexão WebSocket para cada instância (ajuste o IP e a porta conforme necessário)
      const ws = new WebSocket(`ws://${com.ip}:1387`);

// Configura eventos para a conexão WebSocket
ws.onopen = () => {
  console.log(`Connected to WebSocket ${com.ip}`);
  // Envia dados a cada 500 milissegundos
  this.intervals[index_com] = setInterval(() => {
    if(!this.wait_com) {
    this.sendData(index_com, { geral: "1" });

    } else {
      setTimeout(() => {
  this.wait_com = false;
}, 300);
    }
  }, 500);
};

ws.onmessage = (message) => {
  //console.log(message.data);
  if(message.data=="OK") {
    this.genericInputVisible = false;
    if(this.genericInputId != null)
    {
        this.setEdited(this.genericInputId);
    }
  } else {
  this.analise(message.data, index_com);
  }
 // console.log(`Received from ${com.ip}:`, message.data);
};

ws.onerror = (error) => {
  console.error(`WebSocket ${com.ip} Error:`, error);
};

ws.onclose = (event) => {
  console.log(`WebSocket ${com.ip} Closed:`, event);
  clearInterval(this.intervals[index_com]);
};

// Adiciona a instância WebSocket ao array
this.wss.push(ws);
      });
    },
    sendData(index, data) {
      this.wait_com = true;
      setTimeout(() => {
  
      // Verifica se a conexão existe e está aberta
      if (this.wss[index] && this.wss[index].readyState === WebSocket.OPEN) {
        this.wss[index].send(JSON.stringify(data));
      }
    }, 100);
    },
    async postValue(ip, tag, value) {
      // post com axios se deu certo 200 retorna true senao false
      // create obj with tag and value
      let obj = { [tag]: value }
      let r = false;
      await axios
        .post(`http://${ip}/api`, obj)
        .then((response) => {
          console.log(response);
          r = true;
        })
        .catch((error) => {
          console.log(error);

        });
      return r;


    },
    analise(data, index_com) {
      data = JSON.parse(data);
     // console.log(data);


this.prog.element.forEach((el, index) => {
  if (index_com == el.com) {

    if (data[el.tag] != undefined) {
      if (el.type == 'range') {
        let unit = el.unit;
        if (unit == "c") {
          unit = "°C";
        }
        else if (unit == "a") {
          unit = "A";
        } else {
          unit = "";
        }
        this.graph.getCell(index).set('attrs', {
          label: {
            text: data[el.tag] + ' ' + unit
          }
        });
      }

      if (el.type == 'display') {
        let unit = el.unit;
        if (unit == "c") {
          unit = "°C";
        }
        else if (unit == "a") {
          unit = "A";
        } else {
          unit = "";
        }
        let round = this.prog.element[index].round;
        let roundedValue = 0;
        if(round == 0 || round == 1 || round == 2) {
          roundedValue = parseFloat(data[el.tag]).toFixed(round);
        } else {
          roundedValue = data[el.tag];
        }
        
        this.graph.getCell(index).set('attrs', {
          label: {
            text: roundedValue + ' ' + unit
          }
        });
      }

      if (el.type == 'progressbar') {
        var roundedValue = Math.round(data[el.tag]);
        if(el.tag !=""){ 
          this.graph.getCell(index).set('attrs', {
            progress: {
              width: roundedValue
          },
          label: {
            text: roundedValue.toString()+"%"
          }        
        });
        }
      }

      if (el.type == 'button') {
       
       if(el.tag !=""){   
        let fillColor = el.fill;
        let color = el.color;
        let img = "";
        let stroke = el.stroke;
        let label = el.label;
       
        if(data[el.tag] == "1"){
          // enabled
          if(el.label_on) {
          label = el.label_on;
          }
          img = "/img/work.gif";
          fillColor = '#5cb85c'; 
          color= "#fff"; 
          stroke: "#42f542";       
        } else {
          if(el.label_on) {
          label = el.label_off;
          }
          // disabled
          fillColor= "gray";
            color= "#bfbfbf";
            stroke: "gray";
           
        }

        this.graph.getCell(index).set('attrs', {
          body: {
            fill: fillColor,
            stroke: stroke
          },
          label: {
            fill: color,
            text: label,
            textVerticalAnchor: 'middle',
          textAnchor: 'middle',
          },
          image: {
          'xlink:href': img,  // Substitua com o caminho da sua imagem        
        },
          tag: el.tag,
          value: data[el.tag]
        });
       } else {
       
       }
       
      }



    }
  }

});
    },
    fetchData() {
      this.prog["com"].forEach((com, index_com) => {
        let ip = com.ip;
        // faz um get no ip e /api/?return_all com axios e com headers e o method
        axios
          .get(`http://${ip}/api?return_all=1`, {
            headers: {
              'Content-Type': 'application/json',
            },
            method: "GET",
          })
          .then((response) => {

            let data = response.data;
           

            setTimeout(() => {
              this.fetchData();
            }, 500);
          })
          .catch((error) => {
            console.log(error);
          });



      });


    },

    sumGenericInput() {
      this.genericInput += 1;
    }
    ,
    difGenericInput() {
      this.genericInput -= 1;
    },
    async saveGenericInput() {

      // pega o elemento do this.prog pelo id, puxa a comunicação dele e manda pelo ip
      const element = this.prog.element[this.genericInputId];
      const com = this.prog.com[element.com];
      console.log(com.ip);

      let obj = {"cfg":"1"};
        obj[this.genericInputTag] = this.genericInput;    
             
        this.sendData(element.com,obj);
    },
    openInputBox(posX, posY, element) {
      // Cria elementos de entrada e botões
      let inputHtml = `<div style='position:absolute; left:${posX}px; top:${posY}px;'>
                            <input type='text' id='inputValue' value='22' style='width: 50px;'/>
                            <button onclick='increaseValue(${id})'>+</button>
                            <button onclick='decreaseValue(${id})'>-</button>
                         </div>`;
      document.body.innerHTML += inputHtml;
    },
    extrairNumeros(string) {
      // Utiliza uma expressão regular para encontrar a primeira sequência de números na string
      const resultado = string.match(/\d+/);

      // 'match' retorna um array com o resultado ou null se não encontrar nenhum número
      if (resultado) {
        return parseFloat(resultado[0]); // Retorna a primeira sequência de números encontrada
      } else {
        return ''; // Retorna uma string vazia se não houver números
      }
    },
    valueModal(element, size = null) {
      console.log(element);
      const bbox = element.getBBox();
      let x = bbox.x + bbox.width / 2;
      let y = bbox.y + bbox.height / 2;
      const offsetY = -60; // Posição acima do elemento
      const offsetX = 0; // Posição centralizada em relação ao elemento

      let label = this.prog.element[element.model.attributes.id].label;
      let value = this.extrairNumeros(element.model.attributes.attrs.label.text);
      this.genericInputId = element.model.attributes.id;
      this.genericInputTag = this.prog.element[element.model.attributes.id].tag
      this.genericInputLabel = label;
      this.genericInput = value;
      this.genericInputVisible = true;
      const screenWidth = window.innerWidth;
    
      
      // change label color with this.graph.getCell
      if(x+300>screenWidth) {
        
        this.genericInputX = x + offsetX -360;
      } else {
        this.genericInputX = x + offsetX+30;
      }
      
      this.genericInputY = y + offsetY;
      this.setEdit(element.model.attributes.id)
    },
    setEdit(id) {
      this.graph.getCell(id).set('attrs', {
        label: {
          fill: 'blue',
        }
      });
    },
    setEdited(id) {
      this.graph.getCell(id).set('attrs', {
        label: {
          fill: '#000',
          text: "--"
        }
      });
      this.genericInputId = null;
    },
    executeFunction(functionString, element) {
      // Extrai o nome da função e os argumentos da string
      let match = functionString.match(/^(\w+)\((.*)\)$/);
      if (match && typeof this[match[1]] === 'function') {
        // Extrai e processa os argumentos

        let args = match[2].split(',').map(arg => arg.trim().replace(/^'(.*)'$/, '$1'));
        // add element to args
        args.push(element);

        // Chama a função com os argumentos
        this[match[1]].apply(this, args);
      }
    },
    showTooltip(x, y, text) {

    },


    
    toggleDraggable() {
      // this.draggable = !this.draggable;
      // this.$refs.placeholder.style.pointerEvents = this.draggable ? 'auto' : 'none';
    },
    savePositions() {
      const elements = this.graph.getElements();
      const positions = elements.map(el => ({ id: el.id, position: el.position() }));
      console.log(positions);
      localStorage.setItem('elementPositions', JSON.stringify(positions));
    },
    loadPositions() {
      const savedPositions = JSON.parse(localStorage.getItem('elementPositions'));
      console.log(savedPositions);
      if (savedPositions) {
        savedPositions.forEach(pos => {

          const element = this.graph.getCell(pos.id);

          if (element) {

            element.position(pos.position.x, pos.position.y);
          }
        });
      }
    }
  },
  async mounted() {
    console.log("Start");
   
    let dd = {
      "element": "23423"
    }
  // this.$refs.placeholder.style.pointerEvents = 'none';

    this.graph = new joint.dia.Graph();
    const paper = new joint.dia.Paper({
      clickThreshold: 0,
      el: this.$refs.placeholder,
      model: this.graph,
      width: 1366,
      height: 927,
      drawGrid: false,
      gridSize: 10,
      background: {
        color: 'white'
      },
   /*   interactive: function(cellView) {
    if (cellView.model.isLink()) {
      // Permite interações para links (conectores)
      return { vertexAdd: false, vertexMove: false, vertexRemove: false, arrowheadMove: false };
    } else {
      // Desativa o arrasto para todos os elementos
      return { elementMove: false };
    }
  }*/
    });
    let startSelectionPoint = null;

// Capturando o evento mousedown diretamente no papel do JointJS
paper.on('blank:pointerdown', (event, x, y) => {
  this.isSelecting = true;
  startSelectionPoint = { x, y };
  this.selectionBox = { x, y, width: 0, height: 0, visible: true };
});

paper.on('blank:pointermove', (event, x, y) => {
  if (this.isSelecting && startSelectionPoint) {
    const width = x - startSelectionPoint.x;
    const height = y - startSelectionPoint.y;
    this.selectionBox = {
      x: Math.min(x, startSelectionPoint.x), // Usar o menor valor de x
      y: Math.min(y, startSelectionPoint.y), // Usar o menor valor de y
      width: Math.abs(width),
      height: Math.abs(height),
      visible: true
    };
  }
});
let startPos = {};
paper.on('blank:pointerup', (event) => {
  if (this.isSelecting) {
    this.isSelecting = false;
    this.selectionBox.visible = false;

    // Implementação da seleção de elementos
    const elements = this.graph.findModelsInArea({
      x: this.selectionBox.x,
      y: this.selectionBox.y,
      width: this.selectionBox.width,
      height: this.selectionBox.height
    });
    
    if (elements) {
      elements.forEach(element => {
        // Método fictício para manipular a seleção
        this.selectElement(element);
      });
    }
  }
});
paper.on('element:pointermove', (elementView, evt, x, y) => {
  if (startPos.initialized) {
    const deltaX = x - elementView.model.previous('position').x;
    const deltaY = y - elementView.model.previous('position').y;

    this.selectedElements.forEach(id => {
      const element = this.graph.getCell(id);
      const initialPos = startPos[id];
      if (element && initialPos) {
        element.position(initialPos.x + deltaX, initialPos.y + deltaY);
      }
    });
  }
});

paper.on('element:pointerup', () => {
  startPos = {}; // Resetar startPos após o arrasto
  this.savePositions();
});
    paper.on('element:pointerdown', (element, x, y) => {
      if (this.selectedElements.includes(element.model.id)) {
    // Inicializar startPos apenas uma vez no início do arrasto
    if (!startPos.initialized) {
      startPos = this.selectedElements.reduce((acc, id) => {
        const model = this.graph.getCell(id);
        acc[id] = model.position();
        return acc;
      }, {});
      startPos.initialized = true;
    }
  } else {
    // Limpar seleções se clicar fora dos elementos selecionados
    this.selectedElements = [];
    startPos = {};
  }

      console.log(element);
      if (element) {
        try {
          let funcao = element.model.attributes.attrs.click['function'];
          // let funcao = "valueModal('small')";
          this.executeFunction(funcao, element);
        } catch (error) {

        }

        try {
          let mode = element.model.attributes.type;
        
          if (mode == "Range") {
            this.valueModal(element);
          } else if(mode == "ProgressBar") {
            this.valueModal(element);

          }
          
          
          else {
            console.log(element.model.attributes);           

      let id = element.model.attributes.id;
      let value = element.model.attributes.attrs.value;
      let tag = this.prog.element[id].tag
      let com = this.prog.element[id].com;   
      let value_json = this.prog.element[id].value;   
      //let state = this.prog.element[element.model.attributes.id].state;
      console.log(tag); 
      
      if(value_json) {
        let obj = {};
        obj[tag] = value_json;   
        console.log(obj);    
        this.sendData(com,obj );
      } else if(value=="1") {
        let obj = {cfg:"1"};
        obj[tag] = "0";   
        console.log(obj);    
        this.sendData(com,obj );
      } else if(value=="0"){
        let obj = {cfg:"1"};
        obj[tag] = "1";    
        console.log(obj);   
        this.sendData(com,obj );
      }
     
      if(tag!="") {

      }
     
          }
        } catch (error) {

        }


      } else {


      }
    });
    paper.on('selection-box:pointerdown', (elementView, evt) => {
      // Move the selected elements on drag
      if (evt.button === 0 || evt.button === 1) {
        evt.data = { elementView: elementView, startPosition: elementView.model.position() };
        paper.on('mousemove', onMouseMove);
        paper.on('mouseup', onMouseUp, paper);
      }
    });

    function onMouseMove(evt) {
      const data = evt.data;
      const elementView = data.elementView;
      const model = elementView.model;
      const startPosition = data.startPosition;
      const currentScale = paper.scale();
      const dx = (evt.clientX - startPosition.x) / currentScale.sx;
      const dy = (evt.clientY - startPosition.y) / currentScale.sy;
      selection.collection.models.forEach((model) => {
        model.translate(dx, dy);
      });
    }

    function onMouseUp(evt) {
      paper.off('mousemove', onMouseMove);
      paper.off('mouseup', onMouseUp);
    }
    //paper.on('cell:pointerup', (cellView) => {
    //    this.savePositions(); // Salva as posições após arrastar
    // });
   
    const createDisplay = (element, id) => {

      let x = element.x
      let y = element.y
      let title = element.label
      let unit = element.unit;
      let click = element.click;
      let size = element.size;
      let w = element.w;
      let h = element.h;


      let unit_ = "";
      let img = "";
      if (unit == "c") {
        img = "/img/temp.png";
        unit_ = "°C";
      }
      else if (unit == "a") {
        img = "/img/amp.png";
        unit_ = "A";
      }
      else if (unit == "kg") {
        img = "/img/weight.png";
        unit_ = "Kg";
      }
      else {
        img = "/img/meter.png";

      }

      let pw = "60%";
      let ph = "50%";
      if (size == "small") {
        pw = "50%";
        ph = "50%";

      }
      if (size == "medium") {
        pw = "100%";
        ph = "50%";

      }



      //joint.shapes.custom.LcdDisplay = joint.dia.Element.define(
      const LcdDisplay = joint.dia.Element.define('LcdDisplay', {
        //  'custom.LcdDisplay',
        // {
        attrs: {
          body: {
            refWidth: pw,
            refHeight: ph,
            //fill: '#000000',
            stroke: 'blue',
            fillOpacity: 0,
            rx: 6,
            ry: 6
          },
          image: {
            'xlink:href': img,
            width: 20,
            height: 20,
            x: 0,
            y: 2
          },
          label: {
            text: '--' + ' ' + unit_,
            fill: '#000', // Cor do texto
            fontSize: 14,
            refX: 20, // Posição X do texto, à direita do ícone
            refY: 8, // Posição Y do texto, centralizado verticalmente
            textAnchor: 'left'
          },
          title: {
            text: title,
            fill: '#000', // Cor do texto
            fontSize: 6,
            refX: 20, // Posição X do texto, à direita do ícone
            refY: 1, // Posição Y do texto, centralizado verticalmente
            textAnchor: 'left'
          },
          click: {
            'function': click
          }
        }
      },
        {
          markup: [
            {
              tagName: 'rect',
              selector: 'body'
            },
            {
              tagName: 'image',
              selector: 'image'
            },
            {
              tagName: 'text',
              selector: 'label'
            },
            {
              tagName: 'text',
              selector: 'title'
            }
          ]
        }
      );

      // const lcdDisplay = new joint.shapes.custom.LcdDisplay({
      const lcdDisplay = new LcdDisplay({
        position: { x: x, y: y },
        size: { width: 120, height: 50 },
        attrs: { body: { cursor: 'pointer' } }
      });

      lcdDisplay.set('id', id);
      lcdDisplay.addTo(this.graph);
      lcdDisplay.on('element:pointerdown', function (event, x, y) {
        // Cria a interface de entrada acima do LCD Display
        const offsetY = -60; // Posição acima do elemento
        const offsetX = 0; // Posição centralizada em relação ao elemento
        openInputBox(this.position().x + offsetX, this.position().y + offsetY, this);
      });

    }

   
 
      const createProgressBar = (element,id) => {


        let fillColor = element.fill;
  let textColor = element.color;
  let x = element.x
  let y = element.y
  let w = element.w;
  let h = element.h;
  let label = element.label;
  let tag = element.tag;
  let com = element.com;
    const ProgressBar = joint.dia.Element.define('ProgressBar', {
    size: { width: w, height: h },
    position: { x: x, y: y },
    id: id,
    attrs: {
        body: {
            fill: '#E0E0E0',
            stroke: '#000000',
            strokeWidth: 1,
            refWidth: '100%',
            refHeight: '100%'
        },
        progress: {
            fill: '#4CAF50',
            height: h,
            width: 0, // Largura inicial da barra de progresso
            x: 1,
            y: 1
        },
        label: {
            text: '',
            refX: '50%',
            refY: '20%',
            textAnchor: 'middle',
            textVerticalAnchor: 'middle',
            fontSize: 12,
            fill: '#000000'
        }
    }
}, {
    markup: [
        {
            tagName: 'rect',
            selector: 'body'
        },
        {
            tagName: 'rect',
            selector: 'progress'
        },
        {
            tagName: 'text',
            selector: 'label'
        }
    ]
});    

const progress = new ProgressBar({
        position: { x: x, y: y },
        size: { width: w, height: h }       
      });

      progress.set('id', id);
      progress.addTo(this.graph);
     
      return progress;
      }

    const HTMLSwitch = joint.dia.Element.define('HTMLSwitch', {
  size: { width: 70, height: 40 },
  attrs: {
    body: {
      refWidth: '100%',
      refHeight: '100%'
    },
    fo: {
      refWidth: '100%',
      refHeight: '100%',
      tagName: 'foreignObject',
      html: `
        <div xmlns="http://www.w3.org/1999/xhtml" class="switch">
          <input type="checkbox" id="toggle-switch" />
          <label for="toggle-switch" class="slider"></label>
        </div>
      `
    }
  }
}, {
  markup: [
    {
      tagName: 'rect',
      selector: 'body'
    },
    {
      tagName: 'foreignObject',
      selector: 'fo'
    }
  ]
});

function createHTMLSwitch(graph, x, y, id,label) {
  const htmlSwitch = new HTMLSwitch({
    id: id,
    label: label,
    position: { x, y }
  });

  htmlSwitch.addTo(graph);
}


//createHTMLSwitch(this.graph, 100, 200, 5,'switch1');
const createButton = (element,id) => {
  let fillColor = element.fill;
  let textColor = element.color;
  let x = element.x
  let y = element.y
  let w = element.w;
  let h = element.h;
  let label = element.label;
  let tag = element.tag;
  let com = element.com;

      const button = new joint.shapes.standard.Rectangle();
      button.position(x, y);
      // auto resize the button
      button.resize(w, h);      
      button.markup = [
    {
      tagName: 'rect',
      selector: 'body',
    },
    {
      tagName: 'text',
      selector: 'label',
    },
    {
      tagName: 'image',
      selector: 'icon',
    }
  ];

  let way = element.way;
      button.attr({
        body: {
          fill: fillColor,
          rx: 0, // Bordas arredondadas
          ry: 0,
          stroke: "#000",
          strokeWidth: 1,
          cursor: 'default', 
       //   transform: 'rotate(90)'        
        },
        label: {
          text: label,
          fill: textColor,
          fontSize: 14,
          fontWeight: 'bold',
          textVerticalAnchor: 'middle',
          textAnchor: 'middle',
       
        },
        
        image: {
        'xlink:href': "",
        width: 14,
        height: 14,
        refX: 1 , // Posiciona a imagem perto do lado direito
        refY: (h / 2) - 7, // Centraliza verticalmente
            
      }
      }); 
      if(way=="vertical") {
        button.rotate(90);
      }
    
      button.set('id', id);     
      button.addTo(this.graph);
      return button;
    };
    const createRetangle = (element,id) => {
  let fillColor = element.fill;
  let textColor = element.color;
  let x = element.x
  let y = element.y
  let w = element.w;
  let h = element.h;
  let label = element.label;
  let tag = element.tag;
  let com = element.com;

      const button = new joint.shapes.standard.Rectangle();
      button.position(x, y);
      // auto resize the button
      button.resize(w, h);      
      button.markup = [
    {
      tagName: 'rect',
      selector: 'body',
    },
    {
      tagName: 'text',
      selector: 'label',
    },
    {
      tagName: 'image',
      selector: 'icon',
    }
  ];

  let way = element.way;
      button.attr({
        body: {
          fill: "gray",         
          stroke: "#000",
          strokeWidth: 1,
          cursor: 'default', 
       //   transform: 'rotate(90)'        
        },
        label: {
          text: label,
          fill: textColor,
          fontSize: 14,
          fontWeight: 'bold',
          textVerticalAnchor: 'middle',
          textAnchor: 'middle',
       
        },
        
        image: {
        'xlink:href': "",
        width: 14,
        height: 14,
        refX: 1 , // Posiciona a imagem perto do lado direito
        refY: (h / 2) - 7, // Centraliza verticalmente
            
      }
      }); 
      if(way=="vertical") {
        button.rotate(90);
      }
    
      button.set('id', id);     
      button.addTo(this.graph);
      return button;
    };

    const createText = (element,id) => {
  let fillColor = element.fill;
  let textColor = element.color;
  let x = element.x
  let y = element.y
  let w = element.w;
  let h = element.h;
  let label = element.label;
  let tag = element.tag;
  let com = element.com;
  let src = element.src;

      const button = new joint.shapes.standard.Rectangle();
      button.position(x, y);
      // auto resize the button
      button.resize(w, h);      
      button.markup = [
   
    {
      tagName: 'text',
      selector: 'label',
    },
    {
      tagName: 'image',
      selector: 'icon',
    }
  ];
      button.attr({
       
        label: {
          text: label,
          fill: textColor,
          fontSize: 14,
          fontWeight: 'bold',
          textVerticalAnchor: 'middle',
          textAnchor: 'middle'
        },    
       
      }); 
      if(src) {
      button.attr({       
      
       image: {
       'xlink:href': "/img/"+src,
       width: 14,
       height: 14,
       refX: w+12 , // Posiciona a imagem perto do lado direito
       refY: (h / 2) - 7 // Centraliza verticalmente
     }
     });   
    }
      button.set('id', id);     
      button.addTo(this.graph);
      return button;
    };




document.addEventListener('change', function(event) {
  if (event.target.type === 'checkbox') {
    const id = event.target.closest('.joint-cell').getAttribute('model-id');
    const checked = event.target.checked;
    console.log('Switch ID:', id, 'Status:', checked ? 'Enabled' : 'Disabled');
  }
});


    
    const createImage = (element,id) => {

      let x = element.x
let y = element.y
let w = element.w;
let h = element.h;
let src = element.src;
      

      const image = new joint.shapes.standard.Image();
      image.position(x, y);
      image.resize(w, h);
      image.attr({
        body: {
          refWidth: w,
            refHeight: h,
            //fill: '#000000',
            stroke: '#000000',
            fillOpacity: 0,
            rx: 6,
            ry: 6
            },
        image: {
          'xlink:href': '/img/' + src,  // Substitua com o caminho da sua imagem
          width: w,
          height: h
        },
      
      });
      image.set('id', id);
      image.addTo(this.graph);
     
    }
    const createRange = (element, id) => {

      let x = element.x
      let y = element.y
      let title = element.label
      let unit = element.unit;
      let click = element.click;
      let size = element.size;


      let unit_ = "-";
      let img = "";
      if (unit == "c") {
        img = "/img/temp.png";
        unit_ = "°C";
      }
      else if (unit == "a") {
        img = "/img/amp.png";
        unit_ = "A";
      }
      else {
        img = "/img/meter.png";

      }

      let pw = "60%";
      let ph = "50%";
      if (size == "small") {
        pw = "60%";
        ph = "50%";
      }
      //joint.shapes.custom.Range = joint.dia.Element.define(

      // 'custom.Range',
      // {
      const Range = joint.dia.Element.define('Range', {
        attrs: {

          body: {
            refWidth: pw,
            refHeight: ph,
            //fill: '#000000',
            stroke: '#000000',
            fillOpacity: 0,
            rx: 6,
            ry: 6
          },
          image: {
            'xlink:href': img,
            width: 20,
            height: 20,
            x: 0,
            y: 4
          },
          image_edit: {
            'xlink:href': "/img/edit.png",
            width: 20,
            height: 12,
            x: 52,
            y: 8
          },
          label: {

            text: '--',
            fill: '#000', // Cor do texto
            fontSize: 14,
            refX: 20, // Posição X do texto, à direita do ícone
            refY: 8, // Posição Y do texto, centralizado verticalmente
            textAnchor: 'left'
          },
          title: {
            text: title,
            fill: '#000', // Cor do texto
            fontSize: 6,
            refX: 20, // Posição X do texto, à direita do ícone
            refY: 1, // Posição Y do texto, centralizado verticalmente
            textAnchor: 'left'
          },
          click: {
            'function': click
          }
        }
      },
        {
          markup: [
            {
              tagName: 'rect',
              selector: 'body'
            },
            {
              tagName: 'image',
              selector: 'image'
            },
            {
              tagName: 'image',
              selector: 'image_edit'
            },
            {
              tagName: 'text',
              selector: 'label'
            },
            {
              tagName: 'text',
              selector: 'title'
            }
          ]
        }
      );

      // Instância do componente LcdDisplay
      const range = new Range({
        // const Range = new joint.shapes.custom.Range({
        position: { x: x, y: y },
        size: { width: 120, height: 50 },
        attrs: { body: { cursor: 'pointer' } }
      });

      range.set('id', id);
      range.addTo(this.graph);



      //createImage(x-40, y-7, "left_arrow.png", 60, 40, "left_arrow('"+id+")","decrease"); 
      //createImage(x+40, y-7, "right_arrow.png", 60, 40, "right_arrow("+id+")","increase"); 
    }


    // create a joint dialog

    // Função para criar botões estilizados
   


    await axios.get('/ihm/prog.json')
      .then(response => {
        let jbtn = response.data;
        this.prog = jbtn[0];
        let elementos = this.prog["element"];
// Obter uma cópia do array apenas para identificar os clones e evitar modificação durante o loop
const clones = elementos.filter(elemento => elemento.type === "clone");

// Iniciar a busca do primeiro índice do clone
for (let i = 0; i < clones.length; i++) {
  const clone = clones[i];
  // A cada iteração, recalculamos o índice real do clone atual considerando mudanças no array
  let indexClone = elementos.findIndex(elemento => elemento === clone);

  // Encontrar elementos do mesmo grupo que não são clones
  const elementosComClone = elementos.filter(elemento => elemento.group === clone.group && elemento.type !== "clone" && !elemento.cloned);

  // Preparar elementos com os ajustes de posição baseados no clone
  const elementosClonados = elementosComClone.map(elemento => {
    // Verificar se o elemento possui a chave 'label'
    if (elemento.label) {
      // Substituir o número dentro de 'label' especificado por clone.index_old por clone.index
      let labelUpdated = elemento.label.replace(new RegExp(clone.index_old, 'g'), clone.index);
      return {
        ...elemento,
        x: elemento.x + clone.x,
        y: elemento.y + clone.y,
        com: elemento.com + clone.com,
        label: labelUpdated, // Usar o novo valor de label com o número substituído
        cloned: true
      };
    } else {
      return {
        ...elemento,
        x: elemento.x + clone.x,
        y: elemento.y + clone.y,
        com: elemento.com + clone.com,
        cloned: true
      };
    }
  });

  // Remover o clone
  elementos.splice(indexClone, 1);
  // Inserir os elementos clonados ajustados na posição original do clone
  elementos.splice(indexClone, 0, ...elementosClonados);        
}

// Atualizar a lista de elementos no objeto 'this.prog'
this.prog["element"] = elementos;
console.log(this.prog["element"]);


        // iterate jbtn json and create the buttons
        jbtn[0]["element"].forEach((element, index) => {

          if (element["type"] == "button") {
            createButton(element,index);
          }
          if (element["type"] == "image") {
            createImage(element, index);
          }
          if (element["type"] == "display") {
            createDisplay(element, index);
          }
          if (element["type"] == "range") {
            createRange(element, index);
          }
          if (element["type"] == "text") {
            createText(element, index);
          }
          if (element["type"] == "progressbar") {
            createProgressBar(element,index);
          }
          if (element["type"] == "retangle") {
            createRetangle(element,index);
          }
          

          
        


        });
      });


    // Criação dos botões com estilos diferentes
   /* const primaryButton = createButton(100, 500, 'Primary', '#007bff', 'white');
    const secondaryButton = createButton(250, 500, 'Secondary', '#6c757d', 'white');
    const successButton = createButton(400, 500, 'Success', '#28a745', 'white');
    const warningButton = createButton(550, 500, 'Warning', '#ffc107', 'black');
    const dangerButton = createButton(700, 500, 'Danger', '#dc3545', 'white');*/

   





    paper.el.addEventListener('dblclick', this.toggleDraggable);

    //this.loadPositions();
   /* setTimeout(() => {
      this.fetchData();
    }, 0);*/
    // start intervalwith function inside
    setInterval(() => {


      // for each this.prog["com"] for find ip = this.jsonCom.ip
      this.prog["com"].forEach((com, index_com) => {
        if (com.ip == this.jsonCom.ip) {
          this.prog["element"].forEach((element, index_element) => {
            if (element.com == index_com) {
              let id = index_element;

              let unit = element.unit;
              if (id != "0") {

                if (unit == "c") {
                  unit = "°C";
                }
                else if (unit == "a") {
                  unit = "A";
                } else {
                  unit = "";
                }

                this.graph.getCell(id).set('attrs', {
                  label: {
                    text: this.jsonCom.data[element.tag] + ' ' + unit
                  }
                });
              }

            }
          });
        }
      });

    }, 1000);
    this.connect();
 
  },
}
</script>

<style>
#svg-container {
  /* Assumindo que o seu SVG está dentro deste contêiner */
  pointer-events: none;
}

#svg-container svg {
  pointer-events: all;
}

.genericInput {
  width: 300px;
  pointer-events: auto;
  position: absolute;

  background: #e0e0e0;
  color: #333;
  border-radius: 12px;
  padding: 15px;

  z-index: 99999999999;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.inputContainer,
.arrowContainer {
  text-align: center;
}

.big-input {
  font-size: 20px;
  width: 80%;
  padding: 8px;
  border-radius: 8px;
  border: 2px solid #ccc;
}

.arrow {
  width: 80px;
  height: 50px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.arrow:hover {
  transform: scale(1.1);
}

.buttonContainer {
  display: flex;
  justify-content: space-between;
}

.btn-success,
.btn-back {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  padding: 10px;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-success:hover,
.btn-back:hover {
  background-color: #45a049;
}

.btn-back {
  background-color: #6c757d;
  /* Gray color for differentiation */
}

.btn-back:hover {
  background-color: #5a6268;
}

.buttonIcon {
  height: 20px;
}
.textCenter {
  text-align: center;
}


.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:checked + .slider:before {
  transform: translateX(26px);
}
.joint-selection-box {
  border: 2px dashed #333;
}

.joint-handle {
  fill: #5755a1;
  stroke: #5755a1;
}
#svg-container {
  pointer-events: none;
}

#svg-container svg {
  pointer-events: all;
}
.selection-rectangle {
  position: absolute;
  border: 1px dashed #000;
  background-color: rgba(135, 206, 250, 0.3);
  pointer-events: none;
}
</style>