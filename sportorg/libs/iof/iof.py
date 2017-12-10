from abc import abstractmethod
from typing import List
import xml.etree.ElementTree as ET


def indent(elem, level=0):
    """
        import xml.etree.ElementTree as ET

        elem = ET.Element('MyElem')

        indent(elem)
    """
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class BaseElement(object):
    @abstractmethod
    def to_elem(self) -> ET.Element:
        pass

    @staticmethod
    def get_elem(tag, value=None, attr=None, childs=None):
        el = ET.Element(tag)
        if attr is not None:
            el.attrib = attr
        if value is not None:
            el.text = value
        if childs is not None:
            for child in childs:
                if isinstance(child, BaseElement):
                    el.append(child.to_elem())
                else:
                    el.append(child)

        return el

    def write(self, file, **kwargs):
        """
            write(elem, file, encoding='utf-8', xml_declaration=True)
        """
        el = self.to_elem()
        indent(el)
        return ET.ElementTree(el).write(file, **kwargs)


class IOF30(object):
    def __init__(self):
        self.iof_version = 3.0
        self.xmlns = 'http://www.orienteering.org/datastandard/3.0'
        self.xmlns_xsi = 'http://www.w3.org/2001/XMLSchema-instance'
        self.create_time = ''  # 2011-07-20T12:16:31+02:00
        self.creator = ''

    def to_attr(self):
        return {
            'xmlns': self.xmlns,
            'xmlns:xsi': self.xmlns_xsi,
            'iofVersion': str(self.iof_version),
            'createTime': self.create_time,
            'creator': self.creator,
        }


class StartTime(BaseElement):
    def __init__(self):
        self.date = ''  # yyyy-mm-dd
        self.time = ''  # 10:00:00+01:00

    def to_elem(self):
        return self.get_elem(
            'StartTime',
            childs=[
                self.get_elem('Date', self.date),
                self.get_elem('Time', self.time),
            ]
        )


class Event(BaseElement):
    def __init__(self):
        self.name = ''
        self.start_time = StartTime()

    def to_elem(self):
        return self.get_elem(
            'Event',
            childs=[
                self.get_elem('Name', self.name),
                self.start_time,
            ]
        )


class PersonName(BaseElement):
    def __init__(self):
        self.family = ''
        self.given = ''

    def to_elem(self):
        return self.get_elem(
            'Name',
            childs=[
                self.get_elem('Family', self.family),
                self.get_elem('Given', self.given)
            ]
        )


class Person(BaseElement):
    def __init__(self):
        self.id = []  # type: List[str]
        self.name = PersonName()

    def to_elem(self):
        childs = []
        for i in self.id:
            childs.append(self.get_elem('Id', i))
        childs.append(self.name)
        return self.get_elem(
            'Person',
            childs=childs
        )


class Country(BaseElement):
    def __init__(self):
        self.code = ''
        self.name = ''

    def to_elem(self):
        return self.get_elem('Country', self.name, {'code': self.code})


class Organisation(BaseElement):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.country = Country()

    def to_elem(self):
        return self.get_elem(
            'Organisation',
            childs=[
                self.get_elem('Id', self.id),
                self.get_elem('Name', self.name),
                self.country,
            ]
        )


class Class(BaseElement):
    def __init__(self):
        self.id = ''
        self.name = ''

    def to_elem(self):
        return self.get_elem(
            'Class',
            childs=[
                self.get_elem('Id', self.id),
                self.get_elem('Name', self.name)
            ]
        )


class Course(BaseElement):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.length = 0.0
        self.climb = 0.0

    def to_elem(self):
        return self.get_elem(
            'Course',
            childs=[
                self.get_elem('Id', self.id),
                self.get_elem('Name', self.name),
                self.get_elem('Length', str(self.length)),
                self.get_elem('climb', str(self.climb)),
            ]
        )


class PersonEntry(BaseElement):
    def __init__(self):
        self.person = Person()
        self.organisation = Organisation()
        self.control_card = ''
        self.class_ = Class()
        self.entry_time = ''  # 2011-07-12T05:33:17+01:00

    def to_elem(self):
        return self.get_elem(
            'PersonEntry',
            childs=[
                self.person,
                self.organisation,
                self.get_elem('ControlCard', self.control_card),
                self.class_,
                self.get_elem('EntryTime', str(self.entry_time)),
            ]
        )


class EntryList(BaseElement):
    """ET.ElementTree(EntryList().to_elem()).write(file, **kwargs)"""
    def __init__(self):
        self.iof = IOF30()
        self.event = Event()
        self.person_entry = []  # type: List[PersonEntry]

    def to_elem(self):
        childs = [self.event]
        for entry in self.person_entry:
            childs.append(entry)

        return self.get_elem('EntryList', attr=self.iof.to_attr(), childs=childs)


class TeamEntryPerson(BaseElement):
    def __init__(self):
        self.person = Person()
        self.leg = 0
        self.leg_order = 0
        self.control_card = ''

    def to_elem(self):
        return self.get_elem(
            'TeamEntryPerson',
            childs=[
                self.person,
                self.get_elem('Leg', str(self.leg)),
                self.get_elem('LegOrder', str(self.leg_order)),
                self.get_elem('ControlCard', self.control_card)
            ]
        )


class TeamEntry(BaseElement):
    def __init__(self):
        self.name = ''
        self.organisation = Organisation()
        self.team_entry_person = []  # type: List[TeamEntryPerson]
        self.class_ = Class()
        self.entry_time = ''  # 2011-07-12T21:05:58+01:00

    def to_elem(self):
        childs = [self.get_elem('Name', self.name),
                  self.organisation]
        for team in self.team_entry_person:
            childs.append(team)
        childs.append(self.class_)
        childs.append(self.get_elem('EntryTime', self.entry_time))

        return self.get_elem(
            'TeamEntry',
            childs=childs
        )


class TeamEntryList(BaseElement):
    def __init__(self):
        self.iof = IOF30()
        self.event = Event()
        self.team_entry = []  # type: List[TeamEntry]

    def to_elem(self):
        childs = [self.event]
        for entry in self.team_entry:
            childs.append(entry)

        return self.get_elem('EntryList', attr=self.iof.to_attr(), childs=childs)


class PersonStart(BaseElement):
    def __init__(self):
        self.person = Person()
        self.organisation = Organisation()
        self.bib_number = ''
        self.start_time = ''  # 2011-07-30T10:00:00+01:00
        self.control_card = ''

    def to_elem(self):
        return self.get_elem(
            'PersonStart',
            childs=[
                self.person,
                self.organisation,
                self.get_elem('BibNumber', self.bib_number),
                self.get_elem('StartTime', self.start_time),
                self.get_elem('ControlCard', self.control_card)
            ]
        )


class ClassStart(BaseElement):
    def __init__(self):
        self.start_name = ''
        self.class_ = Class()
        self.person_start = []  # type: List[PersonStart]
        self.course = Course()

    def to_elem(self):
        childs = [
            self.get_elem('StartName', self.start_name),
            self.class_,
            self.course
        ]
        for person_start in self.person_start:
            childs.append(person_start)

        return self.get_elem(
            'ClassStart',
            childs=childs
        )


class StartList(BaseElement):
    def __init__(self):
        self.iof = IOF30()
        self.event = Event()
        self.class_start = []  # type: List[ClassStart]

    def to_elem(self):
        childs = [self.event]
        for class_start in self.class_start:
            childs.append(class_start)

        return self.get_elem('StartList', attr=self.iof.to_attr(), childs=childs)


class ResultStatus:
    OK = 'OK'
    FINISHED = 'Finished'
    MISSING_PUNCH = 'MissingPunch'
    DISQUALIFIED = 'Disqualified'
    DID_NOT_FINISH = 'DidNotFinish'
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    OVER_TIME = 'OverTime'
    SPORTING_WITHDRAWAL = 'SportingWithdrawal'
    NOT_COMPETING = 'NotCompeting'
    MOVED = 'Moved'
    MOVED_UP = 'MovedUp'
    DID_NOT_START = 'DidNotStart'
    DID_NOT_ENTER = 'DidNotEnter'
    CANCELLED = 'Cancelled'


class Result(BaseElement):
    def __init__(self):
        self.bib_number = ''
        self.start_time = ''  # 2011-07-30T10:03:00+01:00
        self.finish_time = ''  # 2011-07-30T10:39:42+01:00
        self.time = 0.0
        self.position = []
        self.status = ResultStatus.OK

    def to_elem(self):
        childs = [
            self.get_elem('BibNumber', self.bib_number),
            self.get_elem('StartTime', self.start_time),
            self.get_elem('FinishTime', self.finish_time),
            self.get_elem('Time', str(self.time)),
            self.get_elem('Status', self.status),
        ]
        for pos in self.position:
            childs.append(self.get_elem('Position', str(pos)))
        return self.get_elem(
            'Result',
            childs=childs
        )


class SplitTime(BaseElement):
    def __init__(self):
        self.control_code = ''
        self.time = 0.0

    def to_elem(self):
        return self.get_elem(
            'SplitTime',
            childs=[
                self.get_elem('ControlCode', self.control_code),
                self.get_elem('Time', str(self.time)),
            ]
        )


class Amount(BaseElement):
    def __init__(self):
        self.currency = ''
        self.price = ''

    def to_elem(self):
        return self.get_elem('Amount', self.price, {'currency': self.currency})


class Fee(BaseElement):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.amount = Amount()
        self.taxable_amount = Amount()

    def to_elem(self):
        return self.get_elem(
            'Fee',
            childs=[
                self.get_elem('Id', self.id),
                self.get_elem('Name', self.name),
                self.amount,
                self.taxable_amount
            ]
        )


class AssignedFee(BaseElement):
    def __init__(self):
        self.fee = Fee()
        self.paid_amount = Amount()

    def to_elem(self):
        return self.get_elem(
            'AssignedFee',
            childs=[
                self.fee,
                self.paid_amount
            ]
        )


class Service(BaseElement):
    def __init__(self):
        self.id = ''
        self.name = []

    def to_elem(self):
        childs = [self.get_elem('Id', self.id)]
        for name in self.name:
            childs.append(self.get_elem('Name', name))
        return self.get_elem('Service', childs=childs)


class ServiceRequest(BaseElement):
    def __init__(self):
        self.service = Service()
        self.requested_quantity = 0.0
        self.assigned_fee = []  # type: List[AssignedFee]

    def to_elem(self):
        childs = [
            self.service,
            self.get_elem('RequestedQuantity', str(self.requested_quantity))
        ]
        for assigned_fee in self.assigned_fee:
            childs.append(assigned_fee)
        return self.get_elem('ServiceRequest', childs=childs)


class PersonResult(BaseElement):
    def __init__(self):
        self.person = Person()
        self.organisation = Organisation()
        self.result = Result()
        self.course = Course()
        self.split_time = []  # type: List[SplitTime]
        self.route = ''
        self.assigned_fee = []  # type: List[AssignedFee]
        self.service_request = ServiceRequest()

    def to_elem(self):
        childs = [
            self.person,
            self.organisation,
            self.result,
            self.course,
            self.service_request,
            self.get_elem('Route', self.route)
        ]
        for split in self.split_time:
            childs.append(split)
        for assigned_fee in self.assigned_fee:
            childs.append(assigned_fee)
        return self.get_elem('PersonResult', childs=childs)


class ClassResult(BaseElement):
    def __init__(self):
        self.class_ = Class()
        self.course = Course()
        self.person_result = []  # type: List[PersonResult]

    def to_elem(self):
        childs = [self.class_, self.course]
        for person_result in self.person_result:
            childs.append(person_result)
        return self.get_elem('ClassResult', childs=childs)


class ResultList(BaseElement):
    def __init__(self):
        self.iof = IOF30()
        self.event = Event()
        self.status = ''
        self.class_result = []  # type: List[ClassResult]

    def to_elem(self):
        childs = [self.event, self.get_elem('Status', self.status)]
        for class_result in self.class_result:
            childs.append(class_result)

        return self.get_elem('StartList', attr=self.iof.to_attr(), childs=childs)