/*
 * Tencent is pleased to support the open source community by making
 * 蓝鲸智云PaaS平台 (BlueKing PaaS) available.
 *
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 *
 * 蓝鲸智云PaaS平台 (BlueKing PaaS) is licensed under the MIT License.
 *
 * License for 蓝鲸智云PaaS平台 (BlueKing PaaS):
 *
 * ---------------------------------------------------
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
 * the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */
import { defineComponent, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Popover } from 'bkui-vue';

import { calendarDataConversion, getCalendar, ICalendarData } from './calendar-preview';

import './rotation-calendar-preview.scss';

const mockdata = [
  {
    users: [
      { id: 'xxx', name: 'xxxx' },
      { id: 'xxasdx', name: 'xxasdfxx' }
    ],
    color: '#FF5656',
    timeRange: ['2023-10-4 00:00', '2023-10-4 23:59']
  },
  {
    users: [
      { id: 'xxx', name: 'xxxx' },
      { id: 'xxasdx', name: 'xxasdfxx' }
    ],
    color: '#3A84FF',
    timeRange: ['2023-10-5 00:00', '2023-10-5 23:59']
  },
  {
    users: [
      { id: 'xxx', name: 'xxxx' },
      { id: 'xxasdx', name: 'xxasdfxx' }
    ],
    color: '#FF5656',
    timeRange: ['2023-10-6 00:00', '2023-10-6 23:59']
  },
  {
    users: [
      { id: 'xxx', name: 'xxxx' },
      { id: 'xxasdx', name: 'xxasdfxx' }
    ],
    color: '#3A84FF',
    timeRange: ['2023-10-7 00:00', '2023-10-8 12:00']
  },
  {
    users: [
      { id: 'xxx', name: 'xxxx' },
      { id: 'xxasdx', name: 'xxasdfxx' }
    ],
    color: '#3A84FF',
    timeRange: ['2023-10-18 00:00', '2023-10-18 12:00']
  },
  {
    users: [],
    color: '#FF5656',
    timeRange: ['2023-10-9 00:00', '2023-10-9 23:59']
  },
  {
    users: [],
    color: '#FF5656',
    timeRange: ['2023-10-26 12:00', '2023-10-27 12:59']
  }
];

export default defineComponent({
  name: 'RotationCalendarPreview',
  setup() {
    const { t } = useI18n();
    const contentRef = ref(null);
    /* 当前日历表， 集合了所有日期与用户组的信息 */
    const curCalendarData = ref<ICalendarData>({
      users: mockdata,
      data: getCalendar().map(item => ({
        dates: item,
        data: []
      }))
    });
    /* 日历表头部的 周信息 */
    const weekList = ref([t('周日'), t('周一'), t('周二'), t('周三'), t('周四'), t('周五'), t('周六')]);
    /* 当前容器宽度 */
    const containerWidth = ref(1000);
    const observer = new ResizeObserver(entries => {
      entries.forEach(entry => {
        const { width } = entry.contentRect;
        containerWidth.value = width;
      });
    });
    init();
    /**
     * @description 初始化
     */
    function init() {
      curCalendarData.value = calendarDataConversion(curCalendarData.value);
    }
    onMounted(() => {
      observer.observe(contentRef.value);
    });

    return {
      curCalendarData,
      weekList,
      contentRef,
      containerWidth,
      t
    };
  },
  render() {
    return (
      <div
        class='rotation-calendar-preview-component'
        ref='contentRef'
      >
        <div class='calendar-header'>
          {this.weekList.map(item => (
            <span
              key={item}
              class='week-item'
            >
              {item}
            </span>
          ))}
        </div>
        <div class='calendar-content'>
          {this.curCalendarData.data.map((item, index) => (
            <div
              class='week-row'
              key={index}
            >
              {item.dates.map(date => (
                <div
                  class='day-col'
                  key={date.day}
                >
                  <div
                    class={[
                      'day-label',
                      {
                        check: date.isCurDay,
                        other: date.isOtherMonth
                      }
                    ]}
                  >
                    {date.day === 1 && !date.isCurDay ? this.t('{0}月', [date.month + 1]) : date.day}
                  </div>
                </div>
              ))}
              {item.data.map((data, _index) => (
                <Popover
                  key={`${index}${_index}`}
                  theme='light'
                  placement='top'
                  width={160}
                  arrow={true}
                  extCls={'rotation-calendar-preview-component-user-item-pop'}
                  trigger={'hover'}
                >
                  {{
                    default: () =>
                      !!data.users.length ? (
                        <div
                          class='user-item'
                          style={{
                            width: `${
                              (data?.isStartBorder ? -1 : 0) + this.containerWidth * (data.range[1] - data.range[0])
                            }px`,
                            left: `${(data?.isStartBorder ? 1 : 0) + this.containerWidth * data.range[0]}px`
                          }}
                        >
                          <div
                            class='user-header'
                            style={{ background: data.color }}
                          ></div>
                          <div
                            class='user-content'
                            style={{ color: data.color }}
                          >
                            <span>{data.users.map(u => u.id).join(',')}</span>
                          </div>
                        </div>
                      ) : (
                        <div
                          class='user-item no-user'
                          style={{
                            width: `${
                              (data?.isStartBorder ? -1 : 0) + this.containerWidth * (data.range[1] - data.range[0])
                            }px`,
                            left: `${(data?.isStartBorder ? 1 : 0) + this.containerWidth * data.range[0]}px`
                          }}
                        ></div>
                      ),
                    content: () => (
                      <div class='user-item'>
                        <div class='time'>{data.other.time}</div>
                        <div class='users'>{data.other.users}</div>
                      </div>
                    )
                  }}
                </Popover>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }
});
