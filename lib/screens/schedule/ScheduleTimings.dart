import 'dart:convert';

import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/working_hours.dart';
import 'package:doctro/model/UpdateTiming.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/theme/ayureze_theme.dart';
import 'package:doctro/widgets/osler_button.dart';
import 'package:doctro/widgets/osler_loader.dart';
import 'package:doctro/widgets/osler_toast.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class ScheduleTimings extends StatefulWidget {
  const ScheduleTimings({Key? key}) : super(key: key);

  @override
  _ScheduleTimingsState createState() => _ScheduleTimingsState();
}

//Set Value in Switch
bool isSwitched = true;

//Check Status
int? checkStatus;

List<Data> workingReq = [];
int passIndex = 0;
List startsTime = [];
List endsTime = [];

class _ScheduleTimingsState extends State<ScheduleTimings> {
  //Set Loader
  Future? workingHours;

  List<Map<String, dynamic>> listDynamic = [];

  @override
  void initState() {
    workingHours = doctorWorkingHoursFunction();
    super.initState();
  }

  //Show Start & End Time List
  String? startTime;
  String? endTime;

  //Set Height/Width using MediaQuery
  late double width;
  late double height;

  int? id;

  //Set Value edit Button on Click to addMore
  String? _startTime;
  String? _endTime;

  @override
  Widget build(BuildContext context) {
    width = MediaQuery.of(context).size.width;
    height = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: AyurezeTheme.canvas,
      appBar: AppBar(
        backgroundColor: AyurezeTheme.canvas,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: AyurezeTheme.forestDeep, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          getTranslated(context, AppString.schedule_heading).toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: AyurezeTheme.textPrimary,
          ),
        ),
      ),
      body: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: AyurezeTheme.screenPadding,
        child: FutureBuilder(
            future: workingHours,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return Center(child: CircularProgressIndicator());
              } else {
                return Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: AyurezeTheme.heroDecoration(),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.14),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: const Text(
                              "Weekly availability",
                              style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700),
                            ),
                          ),
                          const SizedBox(height: 14),
                          const Text(
                            "Set your desk hours.",
                            style: TextStyle(color: Colors.white, fontSize: 24, height: 1.05, fontWeight: FontWeight.w800),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            "Define the time slots for each day of the week to let patients know when you're available.",
                            style: TextStyle(color: Colors.white.withOpacity(0.78), fontSize: 14, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 22),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: AyurezeTheme.mutedPanelDecoration(),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            getTranslated(context, AppString.schedule_schedule_title).toString(),
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AyurezeTheme.textSecondary),
                          ),
                          Text(
                            getTranslated(context, AppString.schedule_time_slot).toString(),
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AyurezeTheme.textSecondary),
                          ),
                          Text(
                            getTranslated(context, AppString.schedule_status).toString(),
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AyurezeTheme.textSecondary),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    ListView.builder(
                      itemCount: workingReq.length,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemBuilder: (context, index) {
                        endsTime.clear();
                        startsTime.clear();
                        var parseData = json.decode(workingReq[index].periodList!);
                        for (int i = 0; i < parseData.length; i++) {
                          startsTime.add(parseData[i]['start_time']);
                          endsTime.add(parseData[i]['end_time']);
                        }
                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          decoration: AyurezeTheme.panelDecoration(),
                          child: ListTile(
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            title: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(
                                  flex: 3,
                                  child: Text(
                                    workingReq[index].dayIndex!,
                                    style: TextStyle(fontWeight: FontWeight.w800, color: AyurezeTheme.textPrimary),
                                  ),
                                ),
                                const Spacer(),
                                Expanded(
                                  flex: 8,
                                  child: ListView.builder(
                                    itemCount: startsTime.length,
                                    shrinkWrap: true,
                                    physics: const NeverScrollableScrollPhysics(),
                                    itemBuilder: (context, index) {
                                      return Padding(
                                        padding: const EdgeInsets.only(bottom: 4),
                                        child: Row(
                                          children: [
                                            Text(startsTime[index], style: TextStyle(color: AyurezeTheme.textSecondary, fontSize: 13)),
                                            const SizedBox(width: 4),
                                            Text(getTranslated(context, AppString.to).toString(), style: TextStyle(color: AyurezeTheme.textSecondary, fontSize: 11)),
                                            const SizedBox(width: 4),
                                            Text(endsTime[index], style: TextStyle(color: AyurezeTheme.textSecondary, fontSize: 13)),
                                          ],
                                        ),
                                      );
                                    },
                                  ),
                                ),
                                Expanded(
                                  flex: 2,
                                  child: IconButton(
                                    icon: Icon(Icons.edit_calendar_rounded, color: AyurezeTheme.forestDeep, size: 22),
                                    onPressed: () async {
                                      passIndex = index;
                                      id = workingReq[index].id;
                                      checkStatus = workingReq[index].status;
                                      var convertData;
                                      listDynamic.clear();
                                      convertData = json.decode(workingReq[index].periodList!);
                                      startTime = convertData[0]['start_time'];
                                      endTime = convertData[0]['end_time'];

                                      TextEditingController startController = TextEditingController();
                                      TextEditingController endController = TextEditingController();

                                      for (int k = 0; k < convertData.length; k++) {
                                        startController.text = convertData[k]['start_time'];
                                        endController.text = convertData[k]['end_time'];

                                        listDynamic.add({
                                          "start_time": startController.text,
                                          "end_time": endController.text,
                                        });
                                      }

                                      showDialog(
                                        barrierDismissible: false,
                                        context: context,
                                        builder: (context) {
                                          return StatefulBuilder(
                                            builder: (context, myState) {
                                              return AlertDialog(
                                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
                                                backgroundColor: AyurezeTheme.surface,
                                                title: Column(
                                                  crossAxisAlignment: CrossAxisAlignment.start,
                                                  children: [
                                                    Text(
                                                      getTranslated(context, AppString.schedule_heading).toString(),
                                                      style: const TextStyle(fontWeight: FontWeight.w800),
                                                    ),
                                                    const SizedBox(height: 8),
                                                    SwitchScreen(checkStatus)
                                                  ],
                                                ),
                                                content: Container(
                                                  height: height * 0.4,
                                                  width: width * 0.9,
                                                  child: Column(
                                                    children: [
                                                      Flexible(
                                                        child: ListView.builder(
                                                          itemCount: listDynamic.length,
                                                          itemBuilder: (context, index) {
                                                            return Container(
                                                              margin: const EdgeInsets.only(bottom: 12),
                                                              padding: const EdgeInsets.all(12),
                                                              decoration: BoxDecoration(
                                                                color: AyurezeTheme.surfaceMuted,
                                                                borderRadius: BorderRadius.circular(16),
                                                                border: Border.all(color: AyurezeTheme.border),
                                                              ),
                                                              child: Column(
                                                                children: [
                                                                  Row(
                                                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                    children: [
                                                                      Text(
                                                                        getTranslated(context, AppString.schedule_start_time).toString(),
                                                                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                                                      ),
                                                                      Text(
                                                                        getTranslated(context, AppString.schedule_end_time).toString(),
                                                                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AyurezeTheme.textSecondary),
                                                                      ),
                                                                      const SizedBox(width: 24),
                                                                    ],
                                                                  ),
                                                                  const SizedBox(height: 8),
                                                                  Row(
                                                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                                    children: [
                                                                      InkWell(
                                                                        onTap: () async {
                                                                          List tempChange = [];
                                                                          final TimeOfDay? result = await showTimePicker(
                                                                              context: context,
                                                                              initialTime: TimeOfDay.now(),
                                                                              builder: (context, child) {
                                                                                return MediaQuery(
                                                                                    data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: false),
                                                                                    child: child!);
                                                                              });
                                                                          if (result != null) {
                                                                            myState(() {
                                                                              DateTime tempDate = DateFormat("hh:mm").parse(result.hour.toString() + ":" + result.minute.toString());
                                                                              var dateFormat = DateFormat("hh:mm a");
                                                                              String finalTime = dateFormat.format(tempDate);
                                                                              _startTime = finalTime;

                                                                              var decodeData = json.decode(workingReq[passIndex].periodList!);
                                                                              for (int i = 0; i < listDynamic.length; i++) {
                                                                                tempChange.add(decodeData[i]);
                                                                              }
                                                                              tempChange[index] = {"start_time": _startTime, "end_time": listDynamic[index]["end_time"]};
                                                                              listDynamic[index] = {"start_time": _startTime, "end_time": listDynamic[index]["end_time"]};
                                                                            });
                                                                          }
                                                                          setState(() {
                                                                            workingReq[passIndex].periodList = JsonEncoder().convert(tempChange);
                                                                          });
                                                                        },
                                                                        child: Container(
                                                                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                                                          decoration: BoxDecoration(color: AyurezeTheme.surface, borderRadius: BorderRadius.circular(10), border: Border.all(color: AyurezeTheme.border)),
                                                                          child: Text(listDynamic[index]['start_time'].toString(), style: const TextStyle(fontWeight: FontWeight.w700)),
                                                                        ),
                                                                      ),
                                                                      Icon(Icons.arrow_forward_rounded, size: 16, color: AyurezeTheme.border),
                                                                      InkWell(
                                                                        onTap: () async {
                                                                          List tempChange = [];
                                                                          final TimeOfDay? result = await showTimePicker(
                                                                              context: context,
                                                                              initialTime: TimeOfDay.now(),
                                                                              builder: (context, child) {
                                                                                return MediaQuery(
                                                                                    data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: false),
                                                                                    child: child!);
                                                                              });
                                                                          if (result != null) {
                                                                            myState(() {
                                                                              DateTime tempDate = DateFormat("hh:mm").parse(result.hour.toString() + ":" + result.minute.toString());
                                                                              var dateFormat = DateFormat("hh:mm a");
                                                                              String finalTime = dateFormat.format(tempDate);
                                                                              _endTime = finalTime;

                                                                              var decodeData = json.decode(workingReq[passIndex].periodList!);
                                                                              for (int i = 0; i < listDynamic.length; i++) {
                                                                                tempChange.add(decodeData[i]);
                                                                              }
                                                                              tempChange[index] = {"start_time": listDynamic[index]["start_time"], "end_time": _endTime};
                                                                              listDynamic[index] = {"start_time": listDynamic[index]["start_time"], "end_time": _endTime};
                                                                            });
                                                                          }
                                                                          setState(() {
                                                                            workingReq[passIndex].periodList = JsonEncoder().convert(tempChange);
                                                                          });
                                                                        },
                                                                        child: Container(
                                                                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                                                          decoration: BoxDecoration(color: AyurezeTheme.surface, borderRadius: BorderRadius.circular(10), border: Border.all(color: AyurezeTheme.border)),
                                                                          child: Text(listDynamic[index]['end_time'].toString(), style: const TextStyle(fontWeight: FontWeight.w700)),
                                                                        ),
                                                                      ),
                                                                      if (index != 0)
                                                                        IconButton(
                                                                          icon: Icon(Icons.remove_circle_outline, color: AyurezeTheme.danger, size: 20),
                                                                          onPressed: () {
                                                                            myState(() {
                                                                              listDynamic.removeAt(index);
                                                                            });
                                                                          },
                                                                        )
                                                                      else
                                                                        const SizedBox(width: 48),
                                                                    ],
                                                                  ),
                                                                ],
                                                              ),
                                                            );
                                                          },
                                                        ),
                                                      ),
                                                      const SizedBox(height: 16),
                                                      OutlinedButton.icon(
                                                        onPressed: () {
                                                          myState(() {
                                                            listDynamic.add({
                                                              "start_time": getTranslated(context, AppString.schedule_start_time).toString(),
                                                              "end_time": getTranslated(context, AppString.schedule_end_time).toString(),
                                                            });

                                                            var decodeData = json.decode(workingReq[passIndex].periodList!);
                                                            decodeData.add({
                                                              "start_time": getTranslated(context, AppString.schedule_start_time).toString(),
                                                              "end_time": getTranslated(context, AppString.schedule_end_time).toString(),
                                                            });
                                                            workingReq[passIndex].periodList = JsonEncoder().convert(decodeData);
                                                          });
                                                        },
                                                        icon: const Icon(Icons.add_rounded, size: 18),
                                                        label: Text(getTranslated(context, AppString.schedule_add_more).toString()),
                                                        style: OutlinedButton.styleFrom(
                                                          minimumSize: const Size.fromHeight(48),
                                                          foregroundColor: AyurezeTheme.forestDeep,
                                                          side: BorderSide(color: AyurezeTheme.border),
                                                        ),
                                                      ),
                                                    ],
                                                  ),
                                                ),
actions: <Widget>[
                                                  TextButton(
                                                    child: Text("Cancel", style: TextStyle(color: AyurezeTheme.textSecondary)),
                                                    onPressed: () => Navigator.pop(context),
                                                  ),
                                                  OslerButton(
                                                    text: getTranslated(context, AppString.schedule_ok_button).toString(),
                                                    onPressed: () {
                                                      bool isOk = true;
                                                      for (int i = 0; i < listDynamic.length; i++) {
                                                        if (listDynamic[i]['start_time'] == getTranslated(context, AppString.schedule_start_time).toString() ||
                                                            listDynamic[i]['end_time'] == getTranslated(context, AppString.schedule_end_time).toString()) {
                                                          isOk = false;
                                                        }
                                                      }

                                                      if (isOk == true) {
                                                        myState(() {
                                                          updateHours();
                                                          Navigator.pop(context);
                                                        });
                                                      } else {
                                                        OslerToast.warning(context, getTranslated(context, AppString.please_enter_start_end_time).toString());
                                                      }
                                                    },
                                                  ),
                                                ],
                                              );
                                            },
                                          );
                                        },
                                      );
                                    },
                                  ),
                                )
                              ],
                            ),
                          ),
                        );
                      },
                    )
                  ],
                );
              }
            }),
      ),
    );
  }

  Future<BaseModel<Workinghours>> doctorWorkingHoursFunction() async {
    Workinghours response;

    try {
      workingReq.clear();
      response =
          await RestClient(await RetroApi().dioData(context)).workinghours();
      setState(() {
        workingReq.addAll(response.data!);
      });
    } catch (error, stacktrace) {

      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<UpdateTiming>> updateHours() async {
    List hours = [];

    for (int i = 0; i < listDynamic.length; i++) {
      Map<String, dynamic> mapEducationData = {
        "start_time": listDynamic[i]["start_time"].toString().toLowerCase(),
        "end_time": listDynamic[i]["end_time"].toString().toLowerCase(),
      };
      hours.add(mapEducationData);
    }

    Map<String, dynamic> body = {
      "id": id.toString(),
      "period_list": hours,
      "status": isSwitched == true ? 1 : 0
    };
    UpdateTiming response;
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .updateTimingRequest(body);
      doctorWorkingHoursFunction();
      OslerToast.success(context, response.msg!);
    } catch (error, stacktrace) {

      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }
}

class SwitchScreen extends StatefulWidget {
  SwitchScreen(int? checkStatus);

  @override
  SwitchClass createState() => new SwitchClass();
}

class SwitchClass extends State {
  @override
  void initState() {
    super.initState();
    if (checkStatus == 1) {
      setState(() {
        isSwitched = true;
      });
    } else {
      setState(() {
        isSwitched = false;
      });
    }
  }

  void toggleSwitch(bool value) {
    if (isSwitched == true) {
      setState(() {
        isSwitched = false;
      });
    } else {
      setState(() {
        isSwitched = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(mainAxisAlignment: MainAxisAlignment.center, children: [
      Row(
        children: [
          Container(
            child: Text(getTranslated(context, AppString.schedule_day_status)
                .toString()),
          ),
          Transform.scale(
              scale: 1.2,
              child: Switch(
                onChanged: toggleSwitch,
                value: isSwitched,
                activeColor: colorWhite,
                activeTrackColor: subheading,
                inactiveThumbColor: colorWhite,
                inactiveTrackColor: red,
              )),
        ],
      ),
    ]);
  }
}

