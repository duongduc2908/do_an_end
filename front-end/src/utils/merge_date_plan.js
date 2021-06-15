import store from '@/store'
import moment from "moment";
/**
 * Lưu dữ liệu RepeatConfig theo Ngày
 * Created by thduong 18/12/2020
 */
export function saveRepeatConfigDay() {
  debugger
  let config = {
    DayOfWeek: this.IsWorkingDay == "Chu ky lap" ? false : "MON-FRI",
    RepeatDay: this.num_repeat
  };
  shift_plan.RepeatConfig = config;
}
/**
 * Lưu dữ liệu RepeatConfig theo Tuần
 * Created by thduong 18/12/2020
 */
export function saveRepeatConfigWeek() {

  let DayOfWeek = [];
  this.DayOfWeek.forEach(et => {
    DayOfWeek.push(et.DayValue + 1)
  })
  let config = {
    DayOfWeek: this.DayOfWeek,
    RepeatWeek: this.RepeatWeek
  };
  shift_plan.RepeatConfig = config;
}
/**
 * Lưu dữ liệu RepeatConfig theo Tháng
 * Created by thduong 18/12/2020
 */
export function saveRepeatConfigMonth() {
  let config = {
    RepeatMonth: this.num_repeat,
    WeekOfMonth: this.WeekOfMonth,
    IsDayOfMonth: this.IsDayOfMonth == "Vao" ? false : true
  };
  config.IsDayOfMonth && (config.DayOfMonth = this.DayOfMonth);
  !config.IsDayOfMonth && (config.DayOfWeekNumber = this.DayOfWeekNumber + 1);
  shift_plan.RepeatConfig = config;
}
/**
 * Lấy giá trị ngày đầu tiên của tháng
 * Created by thduong 13/12/2020
 */
export function getFirstDayOfMonth(dateString, dayOfWeek) {
    var date = moment(dateString, "YYYY-MM-DD");

    var day = date.day();
    var diffDays = 0;

    if (day > dayOfWeek) {
      diffDays = 7 - (day - dayOfWeek);
    } else {
      diffDays = dayOfWeek - day;
    }
    return new Date(date.add(diffDays, "day"));
  }
/**
 * Lấy giá trị ngày cuối của tháng
 * Created by thduong 13/12/2020
 */
export function getLastDayOfMonth(dateString, dayOfWeek) {
    var date = moment(dateString, "YYYY-MM-DD");
    var day = date.day();
    var diffDays = 0;
    if (day >= dayOfWeek) {
      diffDays = day - dayOfWeek;
    } else {
      diffDays = 7 - (dayOfWeek - day);
    }
    return new Date(date.add(-diffDays, "day"));
}


export default function createShiftPlan(shift_plan) {
    let listDayScheduler = [];
    let startDate = new Date(shift_plan.FromDate);
    let endDate = new Date(shift_plan.ToDate).setHours(23, 59, 59);

    let config = shift_plan.RepeatConfig
    // Lặp theo ngày
    if (shift_plan.RepeatType == 1) {
      if (!config.DayOfWeek) {
        while (startDate <= endDate) {
          listDayScheduler.push(startDate);
          startDate = moment(startDate)
            .add(config.RepeatDay, "days")
            .toDate();
        }
      }
      // Từ thứ 2 -> thứ 6
      if (config.DayOfWeek) {
        while (startDate <= endDate) {
          if (startDate.getDay() != 0 && startDate.getDay() != 6) {
            listDayScheduler.push(startDate);
          }
          startDate = moment(startDate)
            .add(1, "days")
            .toDate();
        }
      }
    }
    // Lặp theo tuần
    if (shift_plan.RepeatType == 2) {
      if (shift_plan.DateApplyType == 2) {
        // endDate = new Date(this.$refs.MsScheduler.endViewDate);
      }
      config.DayOfWeek.forEach(el => {
          startDate = new Date(shift_plan.FromDate);
          let check = 0;
          while (startDate <= endDate) {
            if (startDate.getDay() == el.DayValue) {
              check++;
              listDayScheduler.push(startDate);
            }
            if (startDate.getDay() == 0 && check > 0) {
              startDate = moment(startDate)
                .add(config.RepeatWeek - 1, "weeks")
                .toDate();
            }
            startDate = moment(startDate)
              .add(1, "days")
              .toDate();
          }
      });
    }
    // Lặp theo tháng
    if (shift_plan.RepeatType == 3) {
      if (shift_plan.DateApplyType == 2) {
        // endDate = new Date(this.$refs.MsScheduler.endViewDate);
      }
      if (!config.IsDayOfMonth) {
        while (startDate <= endDate) {
          let checkDate = new Date();
          if (config.WeekOfMonth == 1) {
            let stringDate = moment(startDate)
              .set("date", 1)
              .toDate();
            checkDate = getFirstDayOfMonth(
              stringDate,
              config.DayOfWeekNumber
            );
          }
          if (config.WeekOfMonth == 5) {
            let stringDate = moment(startDate)
              .endOf("month")
              .toDate();
            checkDate = getLastDayOfMonth(
              stringDate,
              config.DayOfWeekNumber
            );
          }
          if (startDate <= checkDate && checkDate <= endDate) {
            listDayScheduler.push(checkDate);
          }
          startDate = moment(startDate)
            .add(config.RepeatMonth, "months")
            .set("date", 1)
            .toDate();
        }
      }
      if (config.IsDayOfMonth) {
        while (startDate <= endDate) {
          if (startDate.getDate() == config.DayOfMonth) {
            listDayScheduler.push(startDate);
            startDate = moment(startDate)
              .add(config.RepeatMonth, "months")
              .set("date", 1)
              .toDate();
          } else {
            startDate = moment(startDate)
              .add(1, "days")
              .toDate();
          }
        }
      }
    }
    return listDayScheduler
}