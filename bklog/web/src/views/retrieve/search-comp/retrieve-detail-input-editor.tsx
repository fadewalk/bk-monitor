/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

import { Component, PropSync, Emit, Mixins } from 'vue-property-decorator';
import MonacoEditor from '../../../components/collection-access/components/step-add/monaco-editor.vue';
import './retrieve-detail-input-editor.scss';
import classDragMixin from '../../../mixins/class-drag-mixin';

@Component
export default class UiQuery extends Mixins(classDragMixin) {
  @PropSync('value', { type: String, default: '*' }) propsValue: string;
  /** monaco-editor实例 */
  editor = null;
  /** 输入框最小高度 */
  collectMinHeight = 90;
  /** 当前收藏容器的高度 */
  collectHeight = 100;
  /** monaco输入框配置 */
  monacoConfig = {
    cursorBlinking: 'blink',
    acceptSuggestionOnEnter: 'off',
    acceptSuggestionOnCommitCharacter: false, // 是否提示输入
    overviewRulerBorder: false, // 是否应围绕概览标尺绘制边框
    selectOnLineNumbers: false, //
    renderLineHighlight: 'none', // 当前行高亮方式
    lineNumbers: 'off', // 左侧是否展示行
    minimap: {
      enabled: false, // 是否启用预览图
    },
    find: {
      cursorMoveOnType: false,
      seedSearchStringFromSelection: 'never',
      addExtraSpaceOnTop: false,
    },
    // 折叠
    folding: false,
    // 自动换行
    wordWrap: true,
    wrappingStrategy: 'advanced',
    fixedOverflowWidgets: false,
    scrollbar: {
      // 滚动条设置
      verticalScrollbarSize: 6, // 竖滚动条
      useShadows: true, // 失焦阴影动画
    },
    // 隐藏右上角光标的小黑点
    hideCursorInOverviewRuler: true,
    // 隐藏小尺子
    overviewRulerLanes: 0,
  };
  /** 提示样式 */
  placeholderStyle = {
    top: '-1px',
    left: '10px',
    fontSize: '12px',
  };

  @Emit('focus')
  emitFocus() {}

  @Emit('input')
  emitInput(value) {
    return value;
  }

  @Emit('blur')
  emitBlur(value) {
    return value;
  }

  @Emit('keydown')
  emitKeyDown(event) {
    return event;
  }
  focus() {
    const model = this.editor.getModel();
    // 聚焦
    this.editor.focus();
    // 光标跟随
    this.editor.setPosition(model.getPositionAt(model.getValueLength() + 1));
  }
  blur() {
    const model = this.editor.getModel();
    this.editor.blur();
    this.editor.setPosition(model.getPositionAt(model.getValueLength() + 1));
  }
  /** 语法初始化 */
  initMonacoBeforeFun(monaco) {
    monaco.editor.defineTheme('myTheme', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'AND-OR-color', foreground: 'FF9C01' },
        { token: 'NOT-color', foreground: 'CB2427' },
      ],
      colors: {
        'editor.foreground': '63656E', // 用户输入的基础颜色
      },
    });
    monaco.languages.register({ id: 'mySpecialLanguage' });
    monaco.languages.setMonarchTokensProvider('mySpecialLanguage', {
      // 设置语法规则
      tokenizer: {
        root: [
          [/\b(AND|OR)\b/i, 'AND-OR-color'],
          [/\b(NOT)\b/i, 'NOT-color'],
        ],
      },
    });
    // 禁用提示
    monaco.languages.registerCompletionItemProvider('mySpecialLanguage', {
      provideCompletionItems: () => ({ suggestions: [] }),
    });
    return monaco;
  }
  // 获得editor实例
  getEditorInstance(editor) {
    this.editor = editor;
  }

  render() {
    return (
      <div class="retrieve-input-editor">
        <MonacoEditor
          v-model={this.propsValue}
          theme="myTheme"
          language="mySpecialLanguage"
          is-show-top-label={false}
          is-show-problem-drag={false}
          height={this.collectHeight}
          placeholder={this.$t('请输入')}
          placeholder-style={this.placeholderStyle}
          font-size={12}
          monaco-config={this.monacoConfig}
          init-monaco-before-fun={this.initMonacoBeforeFun}
          onChange={this.emitInput}
          onFocus={this.emitFocus}
          onBlur={this.emitBlur}
          onKeydown={this.emitKeyDown}
          onEditorDidMount={editor => this.getEditorInstance(editor)}
        />
        <div
          class={['drag-bottom', { 'drag-ing': this.isChanging }]}
          onMousedown={e => this.dragBegin(e, 'dragY')}
        ></div>
      </div>
    );
  }
}
