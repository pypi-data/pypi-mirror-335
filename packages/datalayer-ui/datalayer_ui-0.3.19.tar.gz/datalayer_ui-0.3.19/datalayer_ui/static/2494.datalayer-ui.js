"use strict";(self.webpackChunk_datalayer_ui=self.webpackChunk_datalayer_ui||[]).push([[2494],{92494:(e,t,a)=>{a.r(t),a.d(t,{default:()=>_a});var o=a(21392),l=a(79557),r=a(83375),n=a(1005),i=a(90519),s=a(54362),u=a(96172),c=a(16909),d=a(98289);function h(e){return d.K.getOrCreate(e).withPrefix("jp")}var g=a(58292),f=a(68500),p=a(52026),m=a(96709),v=a(3473),w=a(82092),b=a(592),F=a(98258),x=a(84486);function V(e){return(0,w.Re)(e)&&"treeitem"===e.getAttribute("role")}class D extends x.I{constructor(){super(...arguments),this.expanded=!1,this.focusable=!1,this.isNestedItem=()=>V(this.parentElement),this.handleExpandCollapseButtonClick=e=>{this.disabled||e.defaultPrevented||(this.expanded=!this.expanded)},this.handleFocus=e=>{this.setAttribute("tabindex","0")},this.handleBlur=e=>{this.setAttribute("tabindex","-1")}}expandedChanged(){this.$fastController.isConnected&&this.$emit("expanded-change",this)}selectedChanged(){this.$fastController.isConnected&&this.$emit("selected-change",this)}itemsChanged(e,t){this.$fastController.isConnected&&this.items.forEach((e=>{V(e)&&(e.nested=!0)}))}static focusItem(e){e.focusable=!0,e.focus()}childItemLength(){const e=this.childItems.filter((e=>V(e)));return e?e.length:0}}(0,g.gn)([(0,p.Lj)({mode:"boolean"})],D.prototype,"expanded",void 0),(0,g.gn)([(0,p.Lj)({mode:"boolean"})],D.prototype,"selected",void 0),(0,g.gn)([(0,p.Lj)({mode:"boolean"})],D.prototype,"disabled",void 0),(0,g.gn)([m.LO],D.prototype,"focusable",void 0),(0,g.gn)([m.LO],D.prototype,"childItems",void 0),(0,g.gn)([m.LO],D.prototype,"items",void 0),(0,g.gn)([m.LO],D.prototype,"nested",void 0),(0,g.gn)([m.LO],D.prototype,"renderCollapsedChildren",void 0),(0,F.e)(D,b.hW);class y extends x.I{constructor(){super(...arguments),this.currentFocused=null,this.handleFocus=e=>{if(!(this.slottedTreeItems.length<1))return e.target===this?(null===this.currentFocused&&(this.currentFocused=this.getValidFocusableItem()),void(null!==this.currentFocused&&D.focusItem(this.currentFocused))):void(this.contains(e.target)&&(this.setAttribute("tabindex","-1"),this.currentFocused=e.target))},this.handleBlur=e=>{e.target instanceof HTMLElement&&(null===e.relatedTarget||!this.contains(e.relatedTarget))&&this.setAttribute("tabindex","0")},this.handleKeyDown=e=>{if(e.defaultPrevented)return;if(this.slottedTreeItems.length<1)return!0;const t=this.getVisibleNodes();switch(e.key){case v.tU:return void(t.length&&D.focusItem(t[0]));case v.Kh:return void(t.length&&D.focusItem(t[t.length-1]));case v.BE:if(e.target&&this.isFocusableElement(e.target)){const t=e.target;t instanceof D&&t.childItemLength()>0&&t.expanded?t.expanded=!1:t instanceof D&&t.parentElement instanceof D&&D.focusItem(t.parentElement)}return!1;case v.mr:if(e.target&&this.isFocusableElement(e.target)){const t=e.target;t instanceof D&&t.childItemLength()>0&&!t.expanded?t.expanded=!0:t instanceof D&&t.childItemLength()>0&&this.focusNextNode(1,e.target)}return;case v.iF:return void(e.target&&this.isFocusableElement(e.target)&&this.focusNextNode(1,e.target));case v.SB:return void(e.target&&this.isFocusableElement(e.target)&&this.focusNextNode(-1,e.target));case v.kL:return void this.handleClick(e)}return!0},this.handleSelectedChange=e=>{if(e.defaultPrevented)return;if(!(e.target instanceof Element&&V(e.target)))return!0;const t=e.target;t.selected?(this.currentSelected&&this.currentSelected!==t&&(this.currentSelected.selected=!1),this.currentSelected=t):t.selected||this.currentSelected!==t||(this.currentSelected=null)},this.setItems=()=>{const e=this.treeView.querySelector("[aria-selected='true']");this.currentSelected=e,null!==this.currentFocused&&this.contains(this.currentFocused)||(this.currentFocused=this.getValidFocusableItem()),this.nested=this.checkForNestedItems(),this.getVisibleNodes().forEach((e=>{V(e)&&(e.nested=this.nested)}))},this.isFocusableElement=e=>V(e),this.isSelectedElement=e=>e.selected}slottedTreeItemsChanged(){this.$fastController.isConnected&&this.setItems()}connectedCallback(){super.connectedCallback(),this.setAttribute("tabindex","0"),f.SO.queueUpdate((()=>{this.setItems()}))}handleClick(e){if(e.defaultPrevented)return;if(!(e.target instanceof Element&&V(e.target)))return!0;const t=e.target;t.disabled||(t.selected=!t.selected)}focusNextNode(e,t){const a=this.getVisibleNodes();if(!a)return;const o=a[a.indexOf(t)+e];(0,w.Re)(o)&&D.focusItem(o)}getValidFocusableItem(){const e=this.getVisibleNodes();let t=e.findIndex(this.isSelectedElement);return-1===t&&(t=e.findIndex(this.isFocusableElement)),-1!==t?e[t]:null}checkForNestedItems(){return this.slottedTreeItems.some((e=>V(e)&&e.querySelector("[role='treeitem']")))}getVisibleNodes(){return(0,w.UM)(this,"[role='treeitem']")||[]}}(0,g.gn)([(0,p.Lj)({attribute:"render-collapsed-nodes"})],y.prototype,"renderCollapsedNodes",void 0),(0,g.gn)([m.LO],y.prototype,"currentSelected",void 0),(0,g.gn)([m.LO],y.prototype,"slottedTreeItems",void 0);var C=a(77407),$=a(86994),I=a(79513),k=a(46594),O=a(91458);const _=class extends y{handleClick(e){if(e.defaultPrevented)return;if(!(e.target instanceof Element))return!0;let t=e.target;for(;t&&!V(t);)t=t.parentElement,t===this&&(t=null);t&&!t.disabled&&(t.selected=!0)}}.compose({baseName:"tree-view",baseClass:y,template:(e,t)=>C.d`
    <template
        role="tree"
        ${(0,$.i)("treeView")}
        @keydown="${(e,t)=>e.handleKeyDown(t.event)}"
        @focusin="${(e,t)=>e.handleFocus(t.event)}"
        @focusout="${(e,t)=>e.handleBlur(t.event)}"
        @click="${(e,t)=>e.handleClick(t.event)}"
        @selected-change="${(e,t)=>e.handleSelectedChange(t.event)}"
    >
        <slot ${(0,I.Q)("slottedTreeItems")}></slot>
    </template>
`,styles:(e,t)=>k.i`
  ${(0,O.j)("flex")} :host {
    flex-direction: column;
    align-items: stretch;
    min-width: fit-content;
    font-size: 0;
  }

  :host:focus-visible {
    outline: none;
  }
`});function T(e,t,a){(0,c.useEffect)((()=>{if(void 0!==a&&e.current&&e.current[t]!==a)try{e.current[t]=a}catch(e){console.warn(e)}}),[a,e.current])}function N(e,t,a){(0,c.useLayoutEffect)((()=>(void 0!==a&&e?.current?.addEventListener(t,a),()=>{a?.cancel&&a.cancel(),e?.current?.removeEventListener(t,a)})),[t,a,e.current])}h().register(_());const H=(0,c.forwardRef)(((e,t)=>{const a=(0,c.useRef)(null),{className:o,renderCollapsedNodes:l,currentSelected:r,...n}=e;return(0,c.useLayoutEffect)((()=>{a.current?.setItems()}),[a.current]),T(a,"currentSelected",e.currentSelected),(0,c.useImperativeHandle)(t,(()=>a.current),[a.current]),c.createElement("jp-tree-view",{ref:a,...n,class:e.className,exportparts:e.exportparts,for:e.htmlFor,part:e.part,tabindex:e.tabIndex,"render-collapsed-nodes":e.renderCollapsedNodes?"":void 0,style:{...e.style}},e.children)}));var L=a(50685),E=a(32018);const S=e=>"function"==typeof e,j=()=>null;function M(e){return void 0===e?j:S(e)?e:()=>e}function A(e,t,a){const o=S(e)?e:()=>e,l=M(t),r=M(a);return(e,t)=>o(e,t)?l(e,t):r(e,t)}var P=a(82553),z=a(50062),B=a(99697),R=a(78390),W=a(22662),U=a(14681),q=a(23137),G=a(63845),K=a(38863),Z=a(3543),Q=a(42953);function J(e,t){const a=e.relativeLuminance>t.relativeLuminance?e:t,o=e.relativeLuminance>t.relativeLuminance?t:e;return(a.relativeLuminance+.05)/(o.relativeLuminance+.05)}const X=Object.freeze({create:(e,t,a)=>new Y(e,t,a),from:e=>new Y(e.r,e.g,e.b)});class Y extends K.h{constructor(e,t,a){super(e,t,a,1),this.toColorString=this.toStringHexRGB,this.contrast=J.bind(null,this),this.createCSS=this.toColorString,this.relativeLuminance=(0,Q.hM)(this)}static fromObject(e){return new Y(e.r,e.g,e.b)}}function ee(e,t,a=0,o=e.length-1){if(o===a)return e[a];const l=Math.floor((o-a)/2)+a;return t(e[l])?ee(e,t,a,l):ee(e,t,l+1,o)}const te=(-.1+Math.sqrt(.21))/2;function ae(e){return e.relativeLuminance<=te}function oe(e){return ae(e)?-1:1}const le=Object.freeze({create:function(e,t,a){return"number"==typeof e?le.from(X.create(e,t,a)):le.from(e)},from:function(e){return function(e){const t={r:0,g:0,b:0,toColorString:()=>"",contrast:()=>0,relativeLuminance:0};for(const a in t)if(typeof t[a]!=typeof e[a])return!1;return!0}(e)?re.from(e):re.from(X.create(e.r,e.g,e.b))}});class re{constructor(e,t){this.closestIndexCache=new Map,this.source=e,this.swatches=t,this.reversedSwatches=Object.freeze([...this.swatches].reverse()),this.lastIndex=this.swatches.length-1}colorContrast(e,t,a,o){void 0===a&&(a=this.closestIndexOf(e));let l=this.swatches;const r=this.lastIndex;let n=a;return void 0===o&&(o=oe(e)),-1===o&&(l=this.reversedSwatches,n=r-n),ee(l,(a=>J(e,a)>=t),n,r)}get(e){return this.swatches[e]||this.swatches[(0,q.uZ)(e,0,this.lastIndex)]}closestIndexOf(e){if(this.closestIndexCache.has(e.relativeLuminance))return this.closestIndexCache.get(e.relativeLuminance);let t=this.swatches.indexOf(e);if(-1!==t)return this.closestIndexCache.set(e.relativeLuminance,t),t;const a=this.swatches.reduce(((t,a)=>Math.abs(a.relativeLuminance-e.relativeLuminance)<Math.abs(t.relativeLuminance-e.relativeLuminance)?a:t));return t=this.swatches.indexOf(a),this.closestIndexCache.set(e.relativeLuminance,t),t}static from(e){return new re(e,Object.freeze(new G.b({baseColor:K.h.fromObject(e)}).palette.map((e=>{const t=(0,Z.in)(e.toStringHexRGB());return X.create(t.r,t.g,t.b)}))))}}const ne=X.create(1,1,1),ie=X.create(0,0,0),se=X.from((0,Z.in)("#808080")),ue=X.from((0,Z.in)("#DA1A5F")),ce=X.from((0,Z.in)("#D32F2F"));function de(e){return X.create(e,e,e)}function he(e,t,a,o,l,r){return Math.max(e.closestIndexOf(de(t))+a,o,l,r)}const{create:ge}=P.L;function fe(e){return P.L.create({name:e,cssCustomPropertyName:null})}const pe=ge("body-font").withDefault('aktiv-grotesk, "Segoe UI", Arial, Helvetica, sans-serif'),me=ge("base-height-multiplier").withDefault(10),ve=(ge("base-horizontal-spacing-multiplier").withDefault(3),ge("base-layer-luminance").withDefault(.23)),we=ge("control-corner-radius").withDefault(4),be=ge("density").withDefault(0),Fe=ge("design-unit").withDefault(4),xe=ge("element-scale").withDefault(0),Ve=ge("direction").withDefault(U.N.ltr),De=ge("disabled-opacity").withDefault(.4),ye=ge("stroke-width").withDefault(1),Ce=ge("focus-stroke-width").withDefault(2),$e=ge("type-ramp-base-font-size").withDefault("14px"),Ie=ge("type-ramp-base-line-height").withDefault("20px"),ke=(ge("type-ramp-minus-1-font-size").withDefault("12px"),ge("type-ramp-minus-1-line-height").withDefault("16px"),ge("type-ramp-minus-2-font-size").withDefault("10px"),ge("type-ramp-minus-2-line-height").withDefault("16px"),ge("type-ramp-plus-1-font-size").withDefault("16px")),Oe=(ge("type-ramp-plus-1-line-height").withDefault("24px"),ge("type-ramp-plus-2-font-size").withDefault("20px"),ge("type-ramp-plus-2-line-height").withDefault("28px"),ge("type-ramp-plus-3-font-size").withDefault("28px"),ge("type-ramp-plus-3-line-height").withDefault("36px"),ge("type-ramp-plus-4-font-size").withDefault("34px"),ge("type-ramp-plus-4-line-height").withDefault("44px"),ge("type-ramp-plus-5-font-size").withDefault("46px"),ge("type-ramp-plus-5-line-height").withDefault("56px"),ge("type-ramp-plus-6-font-size").withDefault("60px"),ge("type-ramp-plus-6-line-height").withDefault("72px"),fe("accent-fill-rest-delta").withDefault(0),fe("accent-fill-hover-delta").withDefault(4)),_e=fe("accent-fill-active-delta").withDefault(-5),Te=fe("accent-fill-focus-delta").withDefault(0),Ne=fe("accent-foreground-rest-delta").withDefault(0),He=fe("accent-foreground-hover-delta").withDefault(6),Le=fe("accent-foreground-active-delta").withDefault(-4),Ee=fe("accent-foreground-focus-delta").withDefault(0),Se=fe("neutral-fill-rest-delta").withDefault(7),je=fe("neutral-fill-hover-delta").withDefault(10),Me=fe("neutral-fill-active-delta").withDefault(5),Ae=fe("neutral-fill-focus-delta").withDefault(0),Pe=fe("neutral-fill-input-rest-delta").withDefault(0),ze=fe("neutral-fill-input-hover-delta").withDefault(0),Be=fe("neutral-fill-input-active-delta").withDefault(0),Re=fe("neutral-fill-input-focus-delta").withDefault(0),We=fe("neutral-fill-stealth-rest-delta").withDefault(0),Ue=fe("neutral-fill-stealth-hover-delta").withDefault(5),qe=fe("neutral-fill-stealth-active-delta").withDefault(3),Ge=fe("neutral-fill-stealth-focus-delta").withDefault(0),Ke=fe("neutral-fill-strong-rest-delta").withDefault(0),Ze=fe("neutral-fill-strong-hover-delta").withDefault(8),Qe=fe("neutral-fill-strong-active-delta").withDefault(-5),Je=fe("neutral-fill-strong-focus-delta").withDefault(0),Xe=fe("neutral-fill-layer-rest-delta").withDefault(3),Ye=fe("neutral-stroke-rest-delta").withDefault(25),et=fe("neutral-stroke-hover-delta").withDefault(40),tt=fe("neutral-stroke-active-delta").withDefault(16),at=fe("neutral-stroke-focus-delta").withDefault(25),ot=fe("neutral-stroke-divider-rest-delta").withDefault(8),lt=ge("neutral-color").withDefault(se),rt=fe("neutral-palette").withDefault((e=>le.from(lt.getValueFor(e)))),nt=ge("accent-color").withDefault(ue),it=fe("accent-palette").withDefault((e=>le.from(nt.getValueFor(e)))),st=fe("neutral-layer-card-container-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=ve.getValueFor(e),o=Xe.getValueFor(e),t.get(t.closestIndexOf(de(a))+o);var t,a,o}}),ut=(ge("neutral-layer-card-container").withDefault((e=>st.getValueFor(e).evaluate(e))),fe("neutral-layer-floating-recipe").withDefault({evaluate:e=>function(e,t,a){const o=e.closestIndexOf(de(t))-a;return e.get(o-a)}(rt.getValueFor(e),ve.getValueFor(e),Xe.getValueFor(e))})),ct=(ge("neutral-layer-floating").withDefault((e=>ut.getValueFor(e).evaluate(e))),fe("neutral-layer-1-recipe").withDefault({evaluate:e=>function(e,t){return e.get(e.closestIndexOf(de(t)))}(rt.getValueFor(e),ve.getValueFor(e))})),dt=ge("neutral-layer-1").withDefault((e=>ct.getValueFor(e).evaluate(e))),ht=fe("neutral-layer-2-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=ve.getValueFor(e),o=Xe.getValueFor(e),l=Se.getValueFor(e),r=je.getValueFor(e),n=Me.getValueFor(e),t.get(he(t,a,o,l,r,n));var t,a,o,l,r,n}}),gt=(ge("neutral-layer-2").withDefault((e=>ht.getValueFor(e).evaluate(e))),fe("neutral-layer-3-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=ve.getValueFor(e),o=Xe.getValueFor(e),l=Se.getValueFor(e),r=je.getValueFor(e),n=Me.getValueFor(e),t.get(he(t,a,o,l,r,n)+o);var t,a,o,l,r,n}})),ft=(ge("neutral-layer-3").withDefault((e=>gt.getValueFor(e).evaluate(e))),fe("neutral-layer-4-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=ve.getValueFor(e),o=Xe.getValueFor(e),l=Se.getValueFor(e),r=je.getValueFor(e),n=Me.getValueFor(e),t.get(he(t,a,o,l,r,n)+2*o);var t,a,o,l,r,n}})),pt=(ge("neutral-layer-4").withDefault((e=>ft.getValueFor(e).evaluate(e))),ge("fill-color").withDefault((e=>dt.getValueFor(e))));var mt;!function(e){e[e.normal=4.5]="normal",e[e.large=7]="large"}(mt||(mt={}));const vt=ge({name:"accent-fill-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>function(e,t,a,o,l,r,n,i,s){const u=e.source,c=t.closestIndexOf(a)>=Math.max(n,i,s)?-1:1,d=e.closestIndexOf(u),h=d+-1*c*o,g=h+c*l,f=h+c*r;return{rest:e.get(h),hover:e.get(d),active:e.get(g),focus:e.get(f)}}(it.getValueFor(e),rt.getValueFor(e),t||pt.getValueFor(e),Oe.getValueFor(e),_e.getValueFor(e),Te.getValueFor(e),Se.getValueFor(e),je.getValueFor(e),Me.getValueFor(e))}),wt=ge("accent-fill-rest").withDefault((e=>vt.getValueFor(e).evaluate(e).rest)),bt=ge("accent-fill-hover").withDefault((e=>vt.getValueFor(e).evaluate(e).hover)),Ft=ge("accent-fill-active").withDefault((e=>vt.getValueFor(e).evaluate(e).active)),xt=ge("accent-fill-focus").withDefault((e=>vt.getValueFor(e).evaluate(e).focus)),Vt=e=>(t,a)=>function(e,t){return e.contrast(ne)>=t?ne:ie}(a||wt.getValueFor(t),e),Dt=fe("foreground-on-accent-recipe").withDefault({evaluate:(e,t)=>Vt(mt.normal)(e,t)}),yt=(ge("foreground-on-accent-rest").withDefault((e=>Dt.getValueFor(e).evaluate(e,wt.getValueFor(e)))),ge("foreground-on-accent-hover").withDefault((e=>Dt.getValueFor(e).evaluate(e,bt.getValueFor(e)))),ge("foreground-on-accent-active").withDefault((e=>Dt.getValueFor(e).evaluate(e,Ft.getValueFor(e)))),ge("foreground-on-accent-focus").withDefault((e=>Dt.getValueFor(e).evaluate(e,xt.getValueFor(e)))),fe("foreground-on-accent-large-recipe").withDefault({evaluate:(e,t)=>Vt(mt.large)(e,t)})),Ct=(ge("foreground-on-accent-rest-large").withDefault((e=>yt.getValueFor(e).evaluate(e,wt.getValueFor(e)))),ge("foreground-on-accent-hover-large").withDefault((e=>yt.getValueFor(e).evaluate(e,bt.getValueFor(e)))),ge("foreground-on-accent-active-large").withDefault((e=>yt.getValueFor(e).evaluate(e,Ft.getValueFor(e)))),ge("foreground-on-accent-focus-large").withDefault((e=>yt.getValueFor(e).evaluate(e,xt.getValueFor(e)))),e=>(t,a)=>function(e,t,a,o,l,r,n){const i=e.source,s=e.closestIndexOf(i),u=oe(t),c=s+(1===u?Math.min(o,l):Math.max(u*o,u*l)),d=e.colorContrast(t,a,c,u),h=e.closestIndexOf(d),g=h+u*Math.abs(o-l);let f,p;return(1===u?o<l:u*o>u*l)?(f=h,p=g):(f=g,p=h),{rest:e.get(f),hover:e.get(p),active:e.get(f+u*r),focus:e.get(f+u*n)}}(it.getValueFor(t),a||pt.getValueFor(t),e,Ne.getValueFor(t),He.getValueFor(t),Le.getValueFor(t),Ee.getValueFor(t))),$t=ge({name:"accent-foreground-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>Ct(mt.normal)(e,t)}),It=ge("accent-foreground-rest").withDefault((e=>$t.getValueFor(e).evaluate(e).rest)),kt=(ge("accent-foreground-hover").withDefault((e=>$t.getValueFor(e).evaluate(e).hover)),ge("accent-foreground-active").withDefault((e=>$t.getValueFor(e).evaluate(e).active)),ge("accent-foreground-focus").withDefault((e=>$t.getValueFor(e).evaluate(e).focus)),ge({name:"neutral-fill-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>function(e,t,a,o,l,r){const n=e.closestIndexOf(t),i=n>=Math.max(a,o,l,r)?-1:1;return{rest:e.get(n+i*a),hover:e.get(n+i*o),active:e.get(n+i*l),focus:e.get(n+i*r)}}(rt.getValueFor(e),t||pt.getValueFor(e),Se.getValueFor(e),je.getValueFor(e),Me.getValueFor(e),Ae.getValueFor(e))})),Ot=ge("neutral-fill-rest").withDefault((e=>kt.getValueFor(e).evaluate(e).rest)),_t=ge("neutral-fill-hover").withDefault((e=>kt.getValueFor(e).evaluate(e).hover)),Tt=ge("neutral-fill-active").withDefault((e=>kt.getValueFor(e).evaluate(e).active)),Nt=(ge("neutral-fill-focus").withDefault((e=>kt.getValueFor(e).evaluate(e).focus)),ge({name:"neutral-fill-input-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>function(e,t,a,o,l,r){const n=oe(t),i=e.closestIndexOf(t);return{rest:e.get(i-n*a),hover:e.get(i-n*o),active:e.get(i-n*l),focus:e.get(i-n*r)}}(rt.getValueFor(e),t||pt.getValueFor(e),Pe.getValueFor(e),ze.getValueFor(e),Be.getValueFor(e),Re.getValueFor(e))})),Ht=(ge("neutral-fill-input-rest").withDefault((e=>Nt.getValueFor(e).evaluate(e).rest)),ge("neutral-fill-input-hover").withDefault((e=>Nt.getValueFor(e).evaluate(e).hover)),ge("neutral-fill-input-active").withDefault((e=>Nt.getValueFor(e).evaluate(e).active)),ge("neutral-fill-input-focus").withDefault((e=>Nt.getValueFor(e).evaluate(e).focus)),ge({name:"neutral-fill-stealth-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>function(e,t,a,o,l,r,n,i,s,u){const c=Math.max(a,o,l,r,n,i,s,u),d=e.closestIndexOf(t),h=d>=c?-1:1;return{rest:e.get(d+h*a),hover:e.get(d+h*o),active:e.get(d+h*l),focus:e.get(d+h*r)}}(rt.getValueFor(e),t||pt.getValueFor(e),We.getValueFor(e),Ue.getValueFor(e),qe.getValueFor(e),Ge.getValueFor(e),Se.getValueFor(e),je.getValueFor(e),Me.getValueFor(e),Ae.getValueFor(e))})),Lt=ge("neutral-fill-stealth-rest").withDefault((e=>Ht.getValueFor(e).evaluate(e).rest)),Et=ge("neutral-fill-stealth-hover").withDefault((e=>Ht.getValueFor(e).evaluate(e).hover)),St=ge("neutral-fill-stealth-active").withDefault((e=>Ht.getValueFor(e).evaluate(e).active)),jt=(ge("neutral-fill-stealth-focus").withDefault((e=>Ht.getValueFor(e).evaluate(e).focus)),ge({name:"neutral-fill-strong-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>function(e,t,a,o,l,r){const n=oe(t),i=e.closestIndexOf(e.colorContrast(t,4.5)),s=i+n*Math.abs(a-o);let u,c;return(1===n?a<o:n*a>n*o)?(u=i,c=s):(u=s,c=i),{rest:e.get(u),hover:e.get(c),active:e.get(u+n*l),focus:e.get(u+n*r)}}(rt.getValueFor(e),t||pt.getValueFor(e),Ke.getValueFor(e),Ze.getValueFor(e),Qe.getValueFor(e),Je.getValueFor(e))})),Mt=(ge("neutral-fill-strong-rest").withDefault((e=>jt.getValueFor(e).evaluate(e).rest)),ge("neutral-fill-strong-hover").withDefault((e=>jt.getValueFor(e).evaluate(e).hover)),ge("neutral-fill-strong-active").withDefault((e=>jt.getValueFor(e).evaluate(e).active)),ge("neutral-fill-strong-focus").withDefault((e=>jt.getValueFor(e).evaluate(e).focus)),fe("neutral-fill-layer-recipe").withDefault({evaluate:(e,t)=>function(e,t,a){const o=e.closestIndexOf(t);return e.get(o-(o<a?-1*a:a))}(rt.getValueFor(e),t||pt.getValueFor(e),Xe.getValueFor(e))})),At=(ge("neutral-fill-layer-rest").withDefault((e=>Mt.getValueFor(e).evaluate(e))),fe("focus-stroke-outer-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=pt.getValueFor(e),t.colorContrast(a,3.5);var t,a}})),Pt=ge("focus-stroke-outer").withDefault((e=>At.getValueFor(e).evaluate(e))),zt=fe("focus-stroke-inner-recipe").withDefault({evaluate:e=>{return t=it.getValueFor(e),a=pt.getValueFor(e),o=Pt.getValueFor(e),t.colorContrast(o,3.5,t.closestIndexOf(t.source),-1*oe(a));var t,a,o}}),Bt=(ge("focus-stroke-inner").withDefault((e=>zt.getValueFor(e).evaluate(e))),fe("neutral-foreground-hint-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=pt.getValueFor(e),t.colorContrast(a,4.5);var t,a}})),Rt=(ge("neutral-foreground-hint").withDefault((e=>Bt.getValueFor(e).evaluate(e))),fe("neutral-foreground-recipe").withDefault({evaluate:e=>{return t=rt.getValueFor(e),a=pt.getValueFor(e),t.colorContrast(a,14);var t,a}})),Wt=ge("neutral-foreground-rest").withDefault((e=>Rt.getValueFor(e).evaluate(e))),Ut=ge({name:"neutral-stroke-recipe",cssCustomPropertyName:null}).withDefault({evaluate:e=>function(e,t,a,o,l,r){const n=e.closestIndexOf(t),i=oe(t),s=n+i*a,u=s+i*(o-a),c=s+i*(l-a),d=s+i*(r-a);return{rest:e.get(s),hover:e.get(u),active:e.get(c),focus:e.get(d)}}(rt.getValueFor(e),pt.getValueFor(e),Ye.getValueFor(e),et.getValueFor(e),tt.getValueFor(e),at.getValueFor(e))}),qt=(ge("neutral-stroke-rest").withDefault((e=>Ut.getValueFor(e).evaluate(e).rest)),ge("neutral-stroke-hover").withDefault((e=>Ut.getValueFor(e).evaluate(e).hover)),ge("neutral-stroke-active").withDefault((e=>Ut.getValueFor(e).evaluate(e).active)),ge("neutral-stroke-focus").withDefault((e=>Ut.getValueFor(e).evaluate(e).focus)),fe("neutral-stroke-divider-recipe").withDefault({evaluate:(e,t)=>function(e,t,a){return e.get(e.closestIndexOf(t)+oe(t)*a)}(rt.getValueFor(e),t||pt.getValueFor(e),ot.getValueFor(e))})),Gt=(ge("neutral-stroke-divider-rest").withDefault((e=>qt.getValueFor(e).evaluate(e))),P.L.create({name:"height-number",cssCustomPropertyName:null}).withDefault((e=>(me.getValueFor(e)+be.getValueFor(e))*Fe.getValueFor(e))),ge("error-color").withDefault(ce)),Kt=fe("error-palette").withDefault((e=>le.from(Gt.getValueFor(e)))),Zt=ge({name:"error-fill-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>function(e,t,a,o,l,r,n,i,s){const u=e.source,c=t.closestIndexOf(a)>=Math.max(n,i,s)?-1:1,d=e.closestIndexOf(u),h=d+-1*c*o,g=h+c*l,f=h+c*r;return{rest:e.get(h),hover:e.get(d),active:e.get(g),focus:e.get(f)}}(Kt.getValueFor(e),rt.getValueFor(e),t||pt.getValueFor(e),Oe.getValueFor(e),_e.getValueFor(e),Te.getValueFor(e),Se.getValueFor(e),je.getValueFor(e),Me.getValueFor(e))}),Qt=ge("error-fill-rest").withDefault((e=>Zt.getValueFor(e).evaluate(e).rest)),Jt=ge("error-fill-hover").withDefault((e=>Zt.getValueFor(e).evaluate(e).hover)),Xt=ge("error-fill-active").withDefault((e=>Zt.getValueFor(e).evaluate(e).active)),Yt=ge("error-fill-focus").withDefault((e=>Zt.getValueFor(e).evaluate(e).focus)),ea=e=>(t,a)=>function(e,t){return e.contrast(ne)>=t?ne:ie}(a||Qt.getValueFor(t),e),ta=ge({name:"foreground-on-error-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>ea(mt.normal)(e,t)}),aa=(ge("foreground-on-error-rest").withDefault((e=>ta.getValueFor(e).evaluate(e,Qt.getValueFor(e)))),ge("foreground-on-error-hover").withDefault((e=>ta.getValueFor(e).evaluate(e,Jt.getValueFor(e)))),ge("foreground-on-error-active").withDefault((e=>ta.getValueFor(e).evaluate(e,Xt.getValueFor(e)))),ge("foreground-on-error-focus").withDefault((e=>ta.getValueFor(e).evaluate(e,Yt.getValueFor(e)))),ge({name:"foreground-on-error-large-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>ea(mt.large)(e,t)})),oa=(ge("foreground-on-error-rest-large").withDefault((e=>aa.getValueFor(e).evaluate(e,Qt.getValueFor(e)))),ge("foreground-on-error-hover-large").withDefault((e=>aa.getValueFor(e).evaluate(e,Jt.getValueFor(e)))),ge("foreground-on-error-active-large").withDefault((e=>aa.getValueFor(e).evaluate(e,Xt.getValueFor(e)))),ge("foreground-on-error-focus-large").withDefault((e=>aa.getValueFor(e).evaluate(e,Yt.getValueFor(e)))),e=>(t,a)=>function(e,t,a,o,l,r,n){const i=e.source,s=e.closestIndexOf(i),u=ae(t)?-1:1,c=s+(1===u?Math.min(o,l):Math.max(u*o,u*l)),d=e.colorContrast(t,a,c,u),h=e.closestIndexOf(d),g=h+u*Math.abs(o-l);let f,p;return(1===u?o<l:u*o>u*l)?(f=h,p=g):(f=g,p=h),{rest:e.get(f),hover:e.get(p),active:e.get(f+u*r),focus:e.get(f+u*n)}}(Kt.getValueFor(t),a||pt.getValueFor(t),e,Ne.getValueFor(t),He.getValueFor(t),Le.getValueFor(t),Ee.getValueFor(t))),la=ge({name:"error-foreground-recipe",cssCustomPropertyName:null}).withDefault({evaluate:(e,t)=>oa(mt.normal)(e,t)}),ra=(ge("error-foreground-rest").withDefault((e=>la.getValueFor(e).evaluate(e).rest)),ge("error-foreground-hover").withDefault((e=>la.getValueFor(e).evaluate(e).hover)),ge("error-foreground-active").withDefault((e=>la.getValueFor(e).evaluate(e).active)),ge("error-foreground-focus").withDefault((e=>la.getValueFor(e).evaluate(e).focus)),k.j`(${me} + ${be} + ${xe}) * ${Fe}`);class na{constructor(e,t){this.cache=new WeakMap,this.ltr=e,this.rtl=t}bind(e){this.attach(e)}unbind(e){const t=this.cache.get(e);t&&Ve.unsubscribe(t)}attach(e){const t=this.cache.get(e)||new ia(this.ltr,this.rtl,e),a=Ve.getValueFor(e);Ve.subscribe(t),t.attach(a),this.cache.set(e,t)}}class ia{constructor(e,t,a){this.ltr=e,this.rtl=t,this.source=a,this.attached=null}handleChange({target:e,token:t}){this.attach(t.getValueFor(e))}attach(e){this.attached!==this[e]&&(null!==this.attached&&this.source.$fastController.removeStyles(this.attached),this.attached=this[e],null!==this.attached&&this.source.$fastController.addStyles(this.attached))}}const sa=k.j`(((${me} + ${be}) * 0.5 + 2) * ${Fe})`,ua=k.i`
  .expand-collapse-glyph {
    transform: rotate(0deg);
  }
  :host(.nested) .expand-collapse-button {
    left: var(
      --expand-collapse-button-nested-width,
      calc(
        (
            ${sa} +
              ((${me} + ${be}) * 1.25)
          ) * -1px
      )
    );
  }
  :host([selected])::after {
    left: calc(${Ce} * 1px);
  }
  :host([expanded]) > .positioning-region .expand-collapse-glyph {
    transform: rotate(90deg);
  }
`,ca=k.i`
  .expand-collapse-glyph {
    transform: rotate(180deg);
  }
  :host(.nested) .expand-collapse-button {
    right: var(
      --expand-collapse-button-nested-width,
      calc(
        (
            ${sa} +
              ((${me} + ${be}) * 1.25)
          ) * -1px
      )
    );
  }
  :host([selected])::after {
    right: calc(${Ce} * 1px);
  }
  :host([expanded]) > .positioning-region .expand-collapse-glyph {
    transform: rotate(90deg);
  }
`,da=P.L.create("tree-item-expand-collapse-hover").withDefault((e=>{const t=Ht.getValueFor(e);return t.evaluate(e,t.evaluate(e).hover).hover})),ha=P.L.create("tree-item-expand-collapse-selected-hover").withDefault((e=>{const t=kt.getValueFor(e);return Ht.getValueFor(e).evaluate(e,t.evaluate(e).rest).hover})),ga=class extends D{}.compose({baseName:"tree-item",baseClass:D,template:(e,t)=>C.d`
    <template
        role="treeitem"
        slot="${e=>e.isNestedItem()?"item":void 0}"
        tabindex="-1"
        class="${e=>e.expanded?"expanded":""} ${e=>e.selected?"selected":""} ${e=>e.nested?"nested":""}
            ${e=>e.disabled?"disabled":""}"
        aria-expanded="${e=>e.childItems&&e.childItemLength()>0?e.expanded:void 0}"
        aria-selected="${e=>e.selected}"
        aria-disabled="${e=>e.disabled}"
        @focusin="${(e,t)=>e.handleFocus(t.event)}"
        @focusout="${(e,t)=>e.handleBlur(t.event)}"
        ${(0,L.p)({property:"childItems",filter:(0,E.R)()})}
    >
        <div class="positioning-region" part="positioning-region">
            <div class="content-region" part="content-region">
                ${A((e=>e.childItems&&e.childItemLength()>0),C.d`
                        <div
                            aria-hidden="true"
                            class="expand-collapse-button"
                            part="expand-collapse-button"
                            @click="${(e,t)=>e.handleExpandCollapseButtonClick(t.event)}"
                            ${(0,$.i)("expandCollapseButton")}
                        >
                            <slot name="expand-collapse-glyph">
                                ${t.expandCollapseGlyph||""}
                            </slot>
                        </div>
                    `)}
                ${(0,b.m9)(e,t)}
                <slot></slot>
                ${(0,b.LC)(e,t)}
            </div>
        </div>
        ${A((e=>e.childItems&&e.childItemLength()>0&&(e.expanded||e.renderCollapsedChildren)),C.d`
                <div role="group" class="items" part="items">
                    <slot name="item" ${(0,I.Q)("items")}></slot>
                </div>
            `)}
    </template>
`,styles:(e,t)=>k.i`
    /**
     * This animation exists because when tree item children are conditionally loaded
     * there is a visual bug where the DOM exists but styles have not yet been applied (essentially FOUC).
     * This subtle animation provides a ever so slight timing adjustment for loading that solves the issue.
     */
    @keyframes treeItemLoading {
      0% {
        opacity: 0;
      }
      100% {
        opacity: 1;
      }
    }

    ${(0,O.j)("block")} :host {
      contain: content;
      position: relative;
      outline: none;
      color: ${Wt};
      background: ${Lt};
      cursor: pointer;
      font-family: ${pe};
      --tree-item-nested-width: 0;
    }

    :host(:focus) > .positioning-region {
      outline: none;
    }

    :host(:focus) .content-region {
      outline: none;
    }

    :host(:${z.b}) .positioning-region {
      border-color: ${xt};
      box-shadow: 0 0 0 calc((${Ce} - ${ye}) * 1px)
        ${xt} inset;
      color: ${Wt};
    }

    .positioning-region {
      display: flex;
      position: relative;
      box-sizing: border-box;
      background: ${Lt};
      border: transparent calc(${ye} * 1px) solid;
      border-radius: calc(${we} * 1px);
      height: calc((${ra} + 1) * 1px);
    }

    .positioning-region::before {
      content: '';
      display: block;
      width: var(--tree-item-nested-width);
      flex-shrink: 0;
    }

    :host(:not([disabled])) .positioning-region:hover {
      background: ${Et};
    }

    :host(:not([disabled])) .positioning-region:active {
      background: ${St};
    }

    .content-region {
      display: inline-flex;
      align-items: center;
      white-space: nowrap;
      width: 100%;
      min-width: 0;
      height: calc(${ra} * 1px);
      margin-inline-start: calc(${Fe} * 2px + 8px);
      font-size: ${$e};
      line-height: ${Ie};
      font-weight: 400;
    }

    .items {
      /* TODO: adaptive typography https://github.com/microsoft/fast/issues/2432 */
      font-size: calc(1em + (${Fe} + 16) * 1px);
    }

    .expand-collapse-button {
      background: none;
      border: none;
      outline: none;
      /* TODO: adaptive typography https://github.com/microsoft/fast/issues/2432 */
      width: calc(${sa} * 1px);
      height: calc(${sa} * 1px);
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      margin-left: 6px;
      margin-right: 6px;
    }

    .expand-collapse-glyph {
      /* TODO: adaptive typography https://github.com/microsoft/fast/issues/2432 */
      width: calc((16 + ${be}) * 1px);
      height: calc((16 + ${be}) * 1px);
      transition: transform 0.1s linear;

      pointer-events: none;
      fill: currentcolor;
    }

    .start,
    .end {
      display: flex;
      fill: currentcolor;
    }

    ::slotted(svg) {
      /* TODO: adaptive typography https://github.com/microsoft/fast/issues/2432 */
      width: 16px;
      height: 16px;

      /* Something like that would do if the typography is adaptive
      font-size: inherit;
      width: ${ke};
      height: ${ke};
      */
    }

    .start {
      /* TODO: horizontalSpacing https://github.com/microsoft/fast/issues/2766 */
      margin-inline-end: calc(${Fe} * 2px + 2px);
    }

    .end {
      /* TODO: horizontalSpacing https://github.com/microsoft/fast/issues/2766 */
      margin-inline-start: calc(${Fe} * 2px + 2px);
    }

    :host([expanded]) > .items {
      animation: treeItemLoading ease-in 10ms;
      animation-iteration-count: 1;
      animation-fill-mode: forwards;
    }

    :host([disabled]) .content-region {
      opacity: ${De};
      cursor: ${B.H};
    }

    :host(.nested) .content-region {
      position: relative;
      /* Add left margin to collapse button size */
      margin-inline-start: calc(
        (
            ${sa} +
              ((${me} + ${be}) * 1.25)
          ) * 1px
      );
    }

    :host(.nested) .expand-collapse-button {
      position: absolute;
    }

    :host(.nested:not([disabled])) .expand-collapse-button:hover {
      background: ${da};
    }

    :host([selected]) .positioning-region {
      background: ${Ot};
    }

    :host([selected]:not([disabled])) .positioning-region:hover {
      background: ${_t};
    }

    :host([selected]:not([disabled])) .positioning-region:active {
      background: ${Tt};
    }

    :host([selected]:not([disabled])) .expand-collapse-button:hover {
      background: ${ha};
    }

    :host([selected])::after {
      /* The background needs to be calculated based on the selected background state
         for this control. We currently have no way of changing that, so setting to
         accent-foreground-rest for the time being */
      background: ${It};
      border-radius: calc(${we} * 1px);
      content: '';
      display: block;
      position: absolute;
      top: calc((${ra} / 4) * 1px);
      width: 3px;
      height: calc((${ra} / 2) * 1px);
    }

    ::slotted(${e.tagFor(D)}) {
      --tree-item-nested-width: 1em;
      --expand-collapse-button-nested-width: calc(
        (
            ${sa} +
              ((${me} + ${be}) * 1.25)
          ) * -1px
      );
    }
  `.withBehaviors(new na(ua,ca),(0,R.vF)(k.i`
      :host {
        forced-color-adjust: none;
        border-color: transparent;
        background: ${W.H.Field};
        color: ${W.H.FieldText};
      }
      :host .content-region .expand-collapse-glyph {
        fill: ${W.H.FieldText};
      }
      :host .positioning-region:hover,
      :host([selected]) .positioning-region {
        background: ${W.H.Highlight};
      }
      :host .positioning-region:hover .content-region,
      :host([selected]) .positioning-region .content-region {
        color: ${W.H.HighlightText};
      }
      :host .positioning-region:hover .content-region .expand-collapse-glyph,
      :host .positioning-region:hover .content-region .start,
      :host .positioning-region:hover .content-region .end,
      :host([selected]) .content-region .expand-collapse-glyph,
      :host([selected]) .content-region .start,
      :host([selected]) .content-region .end {
        fill: ${W.H.HighlightText};
      }
      :host([selected])::after {
        background: ${W.H.Field};
      }
      :host(:${z.b}) .positioning-region {
        border-color: ${W.H.FieldText};
        box-shadow: 0 0 0 2px inset ${W.H.Field};
        color: ${W.H.FieldText};
      }
      :host([disabled]) .content-region,
      :host([disabled]) .positioning-region:hover .content-region {
        opacity: 1;
        color: ${W.H.GrayText};
      }
      :host([disabled]) .content-region .expand-collapse-glyph,
      :host([disabled]) .content-region .start,
      :host([disabled]) .content-region .end,
      :host([disabled])
        .positioning-region:hover
        .content-region
        .expand-collapse-glyph,
      :host([disabled]) .positioning-region:hover .content-region .start,
      :host([disabled]) .positioning-region:hover .content-region .end {
        fill: ${W.H.GrayText};
      }
      :host([disabled]) .positioning-region:hover {
        background: ${W.H.Field};
      }
      .expand-collapse-glyph,
      .start,
      .end {
        fill: ${W.H.FieldText};
      }
      :host(.nested) .expand-collapse-button:hover {
        background: ${W.H.Field};
      }
      :host(.nested) .expand-collapse-button:hover .expand-collapse-glyph {
        fill: ${W.H.FieldText};
      }
    `)),expandCollapseGlyph:'\n        <svg\n            viewBox="0 0 16 16"\n            xmlns="http://www.w3.org/2000/svg"\n            class="expand-collapse-glyph"\n        >\n            <path\n                d="M5.00001 12.3263C5.00124 12.5147 5.05566 12.699 5.15699 12.8578C5.25831 13.0167 5.40243 13.1437 5.57273 13.2242C5.74304 13.3047 5.9326 13.3354 6.11959 13.3128C6.30659 13.2902 6.4834 13.2152 6.62967 13.0965L10.8988 8.83532C11.0739 8.69473 11.2153 8.51658 11.3124 8.31402C11.4096 8.11146 11.46 7.88966 11.46 7.66499C11.46 7.44033 11.4096 7.21853 11.3124 7.01597C11.2153 6.81341 11.0739 6.63526 10.8988 6.49467L6.62967 2.22347C6.48274 2.10422 6.30501 2.02912 6.11712 2.00691C5.92923 1.9847 5.73889 2.01628 5.56823 2.09799C5.39757 2.17969 5.25358 2.30817 5.153 2.46849C5.05241 2.62882 4.99936 2.8144 5.00001 3.00369V12.3263Z"\n            />\n        </svg>\n    '});h().register(ga());const fa=(0,c.forwardRef)(((e,t)=>{const a=(0,c.useRef)(null),{className:o,expanded:l,selected:r,disabled:n,...i}=e;N(a,"expanded-change",e.onExpand),N(a,"selected-change",e.onSelect),T(a,"expanded",e.expanded),T(a,"selected",e.selected),T(a,"disabled",e.disabled),(0,c.useImperativeHandle)(t,(()=>a.current),[a.current]);let s=o??"";return a.current?.nested&&(s+=" nested"),c.createElement("jp-tree-item",{ref:a,...i,class:s.trim(),exportparts:e.exportparts,for:e.htmlFor,part:e.part,tabindex:e.tabIndex,style:{...e.style}},e.children)}));class pa extends c.PureComponent{render(){const{children:e,isActive:t,heading:a,onCollapse:o,onMouseDown:l}=this.props;return c.createElement(fa,{className:"jp-tocItem jp-TreeItem nested",selected:t,expanded:!a.collapsed,onExpand:e=>{e.defaultPrevented||e.target.expanded===!a.collapsed||(e.preventDefault(),o(a))},onMouseDown:e=>{e.defaultPrevented||(e.preventDefault(),l(a))},onKeyUp:e=>{e.defaultPrevented||"Enter"!==e.key||t||(e.preventDefault(),l(a))}},c.createElement("div",{className:"jp-tocItem-heading"},c.createElement("span",{className:"jp-tocItem-content",title:a.text,...a.dataset},a.prefix,a.text)),e)}}class ma extends c.PureComponent{render(){const{documentType:e}=this.props;return c.createElement(H,{className:"jp-TableOfContents-content jp-TreeView","data-document-type":e},this.buildTree())}buildTree(){if(0===this.props.headings.length)return[];const e=t=>{const a=this.props.headings,o=new Array,l=a[t];let r=t+1;for(;r<a.length&&!(a[r].level<=l.level);){const[t,a]=e(r);o.push(t),r=a}return[c.createElement(pa,{key:`${l.level}-${t}-${l.text}`,isActive:!!this.props.activeHeading&&l===this.props.activeHeading,heading:l,onMouseDown:this.props.setActiveHeading,onCollapse:this.props.onCollapseChange},o.length?o:null),r]},t=new Array;let a=0;for(;a<this.props.headings.length;){const[o,l]=e(a);t.push(o),a=l}return t}}class va extends u.UB{constructor(e){super(e.model),this._placeholderHeadline=e.placeholderHeadline,this._placeholderText=e.placeholderText}render(){return this.model&&0!==this.model.headings.length?c.createElement(ma,{activeHeading:this.model.activeHeading,documentType:this.model.documentType,headings:this.model.headings,onCollapseChange:e=>{this.model.toggleCollapse({heading:e})},setActiveHeading:e=>{this.model.setActiveHeading(e)}}):c.createElement("div",{className:"jp-TableOfContents-placeholder"},c.createElement("div",{className:"jp-TableOfContents-placeholderContent"},c.createElement("h3",null,this._placeholderHeadline),c.createElement("p",null,this._placeholderText)))}}class wa extends i.h{constructor(e){super({content:new s.s_,translator:e}),this._model=null,this.addClass("jp-TableOfContents"),this._title=new ba.Header(this._trans.__("Table of Contents")),this.header.addWidget(this._title),this._treeview=new va({placeholderHeadline:this._trans.__("No Headings"),placeholderText:this._trans.__("The table of contents shows headings in notebooks and supported files.")}),this._treeview.addClass("jp-TableOfContents-tree"),this.content.addWidget(this._treeview)}get model(){return this._model}set model(e){var t,a;this._model!==e&&(null===(t=this._model)||void 0===t||t.stateChanged.disconnect(this._onTitleChanged,this),this._model=e,this._model&&(this._model.isActive=this.isVisible),null===(a=this._model)||void 0===a||a.stateChanged.connect(this._onTitleChanged,this),this._onTitleChanged(),this._treeview.model=this._model)}onAfterHide(e){super.onAfterHide(e),this._model&&(this._model.isActive=!1)}onBeforeShow(e){super.onBeforeShow(e),this._model&&(this._model.isActive=!0)}_onTitleChanged(){var e,t;this._title.setTitle(null!==(t=null===(e=this._model)||void 0===e?void 0:e.title)&&void 0!==t?t:this._trans.__("Table of Contents"))}}var ba;!function(e){class t extends s.$L{constructor(e){const t=document.createElement("h2");t.textContent=e,t.classList.add("jp-text-truncated"),super({node:t}),this._title=t}setTitle(e){this._title.textContent=e}}e.Header=t}(ba||(ba={}));class Fa{constructor(){this.modelMapping=new WeakMap}add(e,t){this.modelMapping.set(e,t)}get(e){const t=this.modelMapping.get(e);return!t||t.isDisposed?null:t}}var xa=a(54649);class Va{constructor(){this._generators=new Map,this._idCounter=0}getModel(e,t){for(const a of this._generators.values())if(a.isApplicable(e))return a.createNew(e,t)}add(e){const t=this._idCounter++;return this._generators.set(t,e),new xa.DisposableDelegate((()=>{this._generators.delete(t)}))}}var Da,ya=a(74260),Ca=a(9706),$a=a(74608),Ia=a(32826);!function(e){e.displayNumbering="toc:display-numbering",e.displayH1Numbering="toc:display-h1-numbering",e.displayOutputNumbering="toc:display-outputs-numbering",e.showPanel="toc:show-panel",e.toggleCollapse="toc:toggle-collapse"}(Da||(Da={}));const ka={id:"@jupyterlab/toc-extension:registry",description:"Provides the table of contents registry.",autoStart:!0,provides:n.wk,activate:()=>new Va},Oa={id:"@jupyterlab/toc-extension:tracker",description:"Adds the table of content widget and provides its tracker.",autoStart:!0,provides:n.Ol,requires:[n.wk],optional:[ya.gv,o.L,l.r,r.O],activate:async function(e,t,a,o,l,r){const i=(null!=a?a:ya.Sr).load("jupyterlab");let s={...n.o5.defaultConfig};const u=new wa(null!=a?a:void 0);function c(e){return e.headings.some((e=>{var t;return!(null!==(t=e.collapsed)&&void 0!==t&&t)}))}u.title.icon=Ca.yv,u.title.caption=i.__("Table of Contents"),u.id="table-of-contents",u.node.setAttribute("role","region"),u.node.setAttribute("aria-label",i.__("Table of Contents section")),e.commands.addCommand(Da.displayH1Numbering,{label:i.__("Show first-level heading number"),execute:()=>{u.model&&u.model.setConfiguration({numberingH1:!u.model.configuration.numberingH1})},isEnabled:()=>{var e,t;return null!==(t=null===(e=u.model)||void 0===e?void 0:e.supportedOptions.includes("numberingH1"))&&void 0!==t&&t},isToggled:()=>{var e,t;return null!==(t=null===(e=u.model)||void 0===e?void 0:e.configuration.numberingH1)&&void 0!==t&&t}}),e.commands.addCommand(Da.displayNumbering,{label:i.__("Show heading number in the document"),icon:e=>e.toolbar?Ca.SZ:void 0,execute:()=>{u.model&&(u.model.setConfiguration({numberHeaders:!u.model.configuration.numberHeaders}),e.commands.notifyCommandChanged(Da.displayNumbering))},isEnabled:()=>{var e,t;return null!==(t=null===(e=u.model)||void 0===e?void 0:e.supportedOptions.includes("numberHeaders"))&&void 0!==t&&t},isToggled:()=>{var e,t;return null!==(t=null===(e=u.model)||void 0===e?void 0:e.configuration.numberHeaders)&&void 0!==t&&t}}),e.commands.addCommand(Da.displayOutputNumbering,{label:i.__("Show output headings"),execute:()=>{u.model&&u.model.setConfiguration({includeOutput:!u.model.configuration.includeOutput})},isEnabled:()=>{var e,t;return null!==(t=null===(e=u.model)||void 0===e?void 0:e.supportedOptions.includes("includeOutput"))&&void 0!==t&&t},isToggled:()=>{var e,t;return null!==(t=null===(e=u.model)||void 0===e?void 0:e.configuration.includeOutput)&&void 0!==t&&t}}),e.commands.addCommand(Da.showPanel,{label:i.__("Table of Contents"),execute:()=>{e.shell.activateById(u.id)}}),e.commands.addCommand(Da.toggleCollapse,{label:()=>u.model&&!c(u.model)?i.__("Expand All Headings"):i.__("Collapse All Headings"),icon:e=>e.toolbar?u.model&&!c(u.model)?Ca.L3:Ca.tK:void 0,execute:()=>{u.model&&(c(u.model)?u.model.toggleCollapse({collapsed:!0}):u.model.toggleCollapse({collapsed:!1}))},isEnabled:()=>null!==u.model});const d=new Fa;let h;if(o&&o.add(u,"@jupyterlab/toc:plugin"),r)try{h=await r.load(ka.id);const t=t=>{const a=t.composite;for(const e of[...Object.keys(s)]){const t=a[e];void 0!==t&&(s[e]=t)}if(l)for(const e of l.widgets("main")){const t=d.get(e);t&&t.setConfiguration(s)}else if(e.shell.currentWidget){const t=d.get(e.shell.currentWidget);t&&t.setConfiguration(s)}};h&&(h.changed.connect(t),t(h))}catch(e){console.error(`Failed to load settings for the Table of Contents extension.\n\n${e}`)}const g=new $a.oR({commands:e.commands,id:Da.displayNumbering,args:{toolbar:!0},label:""});g.addClass("jp-toc-numberingButton"),u.toolbar.addItem("display-numbering",g),u.toolbar.addItem("spacer",$a.o8.createSpacerItem()),u.toolbar.addItem("collapse-all",new $a.oR({commands:e.commands,id:Da.toggleCollapse,args:{toolbar:!0},label:""}));const f=new Ia.q({commands:e.commands});f.addItem({command:Da.displayH1Numbering}),f.addItem({command:Da.displayOutputNumbering});const p=new $a.hA({tooltip:i.__("More actions…"),icon:Ca.uW,noFocusOnClick:!1,onClick:()=>{const e=p.node.getBoundingClientRect();f.open(e.x,e.bottom)}});return u.toolbar.addItem("submenu",p),e.shell.add(u,"left",{rank:400,type:"Table of Contents"}),l&&l.currentChanged.connect(m),e.restored.then((()=>{m()})),d;function m(){var a;let o=e.shell.currentWidget;if(!o)return;let l=d.get(o);l||(l=null!==(a=t.getModel(o,s))&&void 0!==a?a:null,l&&d.add(o,l),o.disposed.connect((()=>{null==l||l.dispose()}))),u.model&&(u.model.headingsChanged.disconnect(v),u.model.collapseChanged.disconnect(v)),u.model=l,u.model&&(u.model.headingsChanged.connect(v),u.model.collapseChanged.connect(v)),e.commands.notifyCommandChanged(Da.displayNumbering),e.commands.notifyCommandChanged(Da.toggleCollapse)}function v(){e.commands.notifyCommandChanged(Da.toggleCollapse)}}},_a=[ka,Oa]}}]);