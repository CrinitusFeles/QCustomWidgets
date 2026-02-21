from PyQt6 import QtWidgets


class DateTimeEdit(QtWidgets.QDateTimeEdit):
    _overrideSteps = (
        QtWidgets.QDateTimeEdit.Section.MonthSection,
        QtWidgets.QDateTimeEdit.Section.DaySection,
        QtWidgets.QDateTimeEdit.Section.HourSection,
        QtWidgets.QDateTimeEdit.Section.MinuteSection,
        QtWidgets.QDateTimeEdit.Section.SecondSection,
    )
    def stepEnabled(self):
        if self.currentSection() in self._overrideSteps:
            return self.StepEnabledFlag.StepUpEnabled | self.StepEnabledFlag.StepDownEnabled
        return super().stepEnabled()

    def stepBy(self, steps):
        section = self.currentSection()
        if section not in self._overrideSteps:
            super().stepBy(steps)
            return
        dt = self.dateTime()
        section = self.currentSection()
        if section == self.Section.MonthSection:
            dt = dt.addMonths(steps)
        elif section == self.Section.DaySection:
            dt = dt.addDays(steps)
        elif section == self.Section.HourSection:
            dt = dt.addSecs(3600 * steps)
        elif section == self.Section.MinuteSection:
            dt = dt.addSecs(60 * steps)
        else:
            dt = dt.addSecs(steps)
        self.setDateTime(dt)
