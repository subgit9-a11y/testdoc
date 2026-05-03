import 'dart:developer';

import 'package:agora_rtc_engine/agora_rtc_engine.dart';
import 'package:doctro/VideoCall/overlay_handler.dart';
import 'package:doctro/VideoCall/overlay_service.dart';
import 'package:doctro/constant/app_icons.dart';
import 'package:doctro/constant/app_string.dart';
import 'package:doctro/constant/color_constant.dart';
import 'package:doctro/constant/prefConstatnt.dart';
import 'package:doctro/constant/preferences.dart';
import 'package:doctro/localization/localization_constant.dart';
import 'package:doctro/model/doctor_profile.dart';
import 'package:doctro/model/setting.dart';
import 'package:doctro/model/video_call_history_add_model.dart';
import 'package:doctro/retrofit/api_header.dart';
import 'package:doctro/retrofit/base_model.dart';
import 'package:doctro/retrofit/network_api.dart';
import 'package:doctro/retrofit/server_error.dart';
import 'package:doctro/screens/home page/login_home.dart';
import 'package:doctro/screens/videoCall/model/doctorAgoraTokenGenerateModel.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:intl/intl.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:pip_view/pip_view.dart';
import 'package:progress_indicators/progress_indicators.dart';
import 'package:provider/provider.dart';

import '../../helpers/logger.dart';

class VideoCall extends StatefulWidget {
  final bool callEnd;
  final int? id;
  final String? flag;

  VideoCall({
    required this.callEnd,
    this.id,
    this.flag,
  });
  @override
  _VideoCallState createState() => _VideoCallState();
}

class _VideoCallState extends State<VideoCall> {
  int? _remoteUid;
  bool _localUserJoined = false;
  bool muted = false;
  bool mutedVideo = false;
  late RtcEngine _engine;
  String? appId;
  int uid = 0;
  String? token;
  String? channelName;
  int? doctorId = 0;
  ChannelMediaOptions options = const ChannelMediaOptions(
    clientRoleType: ClientRoleType.clientRoleBroadcaster,
    channelProfile: ChannelProfileType.channelProfileCommunication,
  );

  int? callDuration = 0;
  String? callTime = "";
  String? callDate = "";

  @override
  void initState() {
    log("Call End : ${widget.callEnd}\tID : ${widget.id}\tFlag : ${widget.flag}");
    super.initState();
    settingRequest();
    offset = const Offset(20.0, 50.0);
  }

  Offset offset = Offset.zero;
  int? boxNumberIsDragged;

  Widget _toolbar() {
    return Consumer<OverlayHandlerProvider>(
      builder: (context, overlayProvider, _) {
        return Align(
          alignment: Alignment.bottomCenter,
          child: Container(
            margin: const EdgeInsets.only(bottom: 30),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.4),
              borderRadius: BorderRadius.circular(30),
              border: Border.all(color: Colors.white.withOpacity(0.2), width: 1),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                // Mute Audio
                _buildControlButton(
                  onPressed: _onToggleMute,
                  icon: muted ? Icons.mic_off : Icons.mic,
                  color: muted ? Colors.red : Colors.white,
                  bgColor: muted ? Colors.white : Colors.white.withOpacity(0.2),
                ),
                const SizedBox(width: 15),
                
                // Mute Video
                _buildControlButton(
                  onPressed: _onToggleVideo,
                  icon: mutedVideo ? Icons.videocam_off : Icons.videocam,
                  color: mutedVideo ? Colors.red : Colors.white,
                  bgColor: mutedVideo ? Colors.white : Colors.white.withOpacity(0.2),
                ),
                const SizedBox(width: 15),

                // Switch Camera
                _buildControlButton(
                  onPressed: _onSwitchCamera,
                  icon: Icons.flip_camera_ios_outlined,
                  color: Colors.white,
                  bgColor: Colors.white.withOpacity(0.2),
                ),
                const SizedBox(width: 25),

                // End Call
                GestureDetector(
                  onTap: () => _onCallEnd(context),
                  child: Container(
                    height: 55,
                    width: 55,
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))
                      ],
                    ),
                    child: const Icon(Icons.call_end, color: Colors.white, size: 28),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildControlButton({
    required VoidCallback onPressed,
    required IconData icon,
    required Color color,
    required Color bgColor,
  }) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        height: 48,
        width: 48,
        decoration: BoxDecoration(
          color: bgColor,
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: color, size: 22),
      ),
    );
  }

  void _onToggleVideo() {
    setState(() {
      mutedVideo = !mutedVideo;
      _engine.muteLocalVideoStream(mutedVideo);
    });
  }
  void _onCallEnd(BuildContext context) {
    try {
      setState(() {
        _localUserJoined = false;
        _remoteUid = null;
        _engine.leaveChannel();
      });
    } catch (e) {
      logger.e(e);
    }
    Navigator.pop(context);
  }

  void _onToggleMute() {
    setState(() {
      muted = !muted;
      _engine.muteLocalAudioStream(muted);
    });
  }

  void _onSwitchCamera() {
    setState(() {
      _engine.switchCamera();
    });
  }

  Future<void> initAgora() async {
    try {
      var statuses = await [
        Permission.camera,
        Permission.microphone,
      ].request();
      if (statuses[Permission.camera] != PermissionStatus.granted ||
          statuses[Permission.microphone] != PermissionStatus.granted) {
        throw Exception('Camera or Microphone permission not granted');
      }
      _engine = await createAgoraRtcEngine();
      await _engine.initialize(RtcEngineContext(
          appId: appId != null
              ? appId
              : SharedPreferenceHelper.getString(Preferences.agoraAppId)));
      await _engine.enableVideo();
      await _engine.setVideoEncoderConfiguration(
        const VideoEncoderConfiguration(
          dimensions: VideoDimensions(width: 640, height: 360),
          frameRate: 15,
          bitrate: 0,
          orientationMode: OrientationMode.orientationModeFixedPortrait,
        ),
      );

      _engine.registerEventHandler(
        RtcEngineEventHandler(
          onJoinChannelSuccess: (RtcConnection connection, int elapsed) {
            log("Local user uid : ${connection.localUid} joined the channel");
            setState(() {
              _localUserJoined = true;
            });
          },
          onUserJoined: (RtcConnection connection, int remoteUid, int elapsed) {
            log("Remote user uid:$remoteUid joined the channel");
            DateTime now = DateTime.now();
            callTime = DateFormat('h:mm a').format(now);
            callDate = DateFormat('yyyy-MM-dd').format(now);
            setState(() {
              _remoteUid = remoteUid;
            });
          },
          onUserOffline: (RtcConnection connection, int remoteUid,
              UserOfflineReasonType reason) {
            setState(() {
              _remoteUid = null;
              _engine.leaveChannel();
              Fluttertoast.showToast(
                  msg: "Call Ended", toastLength: Toast.LENGTH_SHORT);
            });
          },
          onLeaveChannel: (RtcConnection connection, RtcStats details) {
            setState(() {
              if (widget.flag == "OutGoing") {
                callDuration = details.duration;
                OverlayService().removeVideosOverlay(
                    context,
                    VideoCall(
                      id: widget.id,
                      callEnd: false,
                    ));
              } else {
                callDuration = details.duration;
                if (callTime != "" &&
                    callDate != "" &&
                    widget.callEnd == false) {
                  callApiAddVideoCallHistory();
                  Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                          builder: (context) => LoginHomeScreen(chat: "")));
                } else {
                  Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                          builder: (context) => LoginHomeScreen(chat: "")));
                }
              }
            });
          },
        ),
      );
      if (token != null && channelName != null && token!.isNotEmpty && channelName!.isNotEmpty) {
        await _engine.startPreview();
        _engine.joinChannel(
          token: '$token',
          channelId: '$channelName',
          uid: uid,
          options: options,
        );
      }
    } catch (e) {
      logger.e(e);
    }
  }

  @override
  void dispose() async {
    super.dispose();
    await _engine.leaveChannel();
    await _engine.release();
  }

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;
    double height = MediaQuery.of(context).size.height;

    return PIPView(
      builder: (context, isFloating) {
        return Scaffold(
          backgroundColor: const Color(0xFF1A1A1A),
          body: Consumer<OverlayHandlerProvider>(
            builder: (context, overlayProvider, _) {
              return Stack(
                children: [
                  // Remote Video (Background)
                  Positioned.fill(
                    child: _remoteVideo(),
                  ),

                  // Top Status Bar (Duration / Name)
                  if (_remoteUid != null)
                    Positioned(
                      top: 50,
                      left: 0,
                      right: 0,
                      child: Center(
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.black38,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 8,
                                height: 8,
                                decoration: const BoxDecoration(
                                  color: Colors.red,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                "Live Consultation",
                                style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),

                  // Local Preview (Floating)
                  if (!widget.callEnd)
                    Positioned(
                      right: 20,
                      top: 100,
                      child: GestureDetector(
                        onPanUpdate: (details) {
                          setState(() {
                            // Boundary checks
                            double newX = offset.dx + details.delta.dx;
                            double newY = offset.dy + details.delta.dy;
                            if (newX > 0 && newX < width - 120 && newY > 0 && newY < height - 160) {
                              offset = Offset(newX, newY);
                            }
                          });
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 120,
                          height: 160,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: Colors.white.withOpacity(0.3), width: 1.5),
                            boxShadow: const [
                              BoxShadow(color: Colors.black45, blurRadius: 10, spreadRadius: 2)
                            ],
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(15),
                            child: _localUserJoined && !mutedVideo
                                ? _localPreview()
                                : Container(
                                    color: Colors.grey[900],
                                    child: const Icon(Icons.videocam_off, color: Colors.white38, size: 30),
                                  ),
                          ),
                        ),
                      ),
                    ),

                  // Bottom Toolbar
                  _toolbar(),
                ],
              );
            },
          ),
        );
      },
    );
  }

  Future<BaseModel<DoctorProfile>> doctorProfile() async {
    DoctorProfile response;
    try {
      response =
          await RestClient(await RetroApi().dioData(context)).doctorProfile();
      if (response.success == true) {
        token = response.data!.agoraToken;
        channelName = response.data!.channelName;
        doctorId = response.data!.id;
        await initAgora();
      }
      setState(() {});
    } catch (error, stacktrace) {
      log("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<void> agoraTokenGenerateDoctor() async {
    VideoCallModel response;
    Map<String, dynamic> body = {"to_id": widget.id};
    log("body  = $body");
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .generateDoctorAgoraTokenCall(body);
      if (response.success == true) {
        channelName = response.data!.cn;
        token = response.data!.token;
        await initAgora();
        setState(() {});
      } else {
        Fluttertoast.showToast(msg: "Failed to call the patient! Unable to connect!");
        Navigator.pop(context);
      }
    } catch (error, stacktrace) {
      Fluttertoast.showToast(msg: "Failed to call the patient! Unable to connect!");
      Navigator.pop(context);
    }
  }

  Future<BaseModel<Setting>> settingRequest() async {
    Setting response;
    try {
      response =
          await RestClient(await RetroApi().dioData(context)).settingRequest();

      appId = response.data!.agoraAppId;
      if (widget.flag != "OutGoing") {
        await doctorProfile();
      } else {
        await agoraTokenGenerateDoctor();
      }
      setState(() {});
    } catch (error, stacktrace) {
      logger.e("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Future<BaseModel<VideoCallHistoryAddModel>>
      callApiAddVideoCallHistory() async {
    VideoCallHistoryAddModel response;
    Map<String, dynamic> body = {
      "user_id": widget.id,
      "date": callDate,
      "start_time": callTime,
      "duration": callDuration,
      "doctor_id": doctorId,
    };
    try {
      response = await RestClient(await RetroApi().dioData(context))
          .videoCallHistoryAddRequest(body);
    } catch (error, stacktrace) {
      log("Exception occur: $error stackTrace: $stacktrace");
      return BaseModel()..setException(ServerError.withError(error: error));
    }
    return BaseModel()..data = response;
  }

  Widget _localPreview() {
    return AgoraVideoView(
      controller: VideoViewController(
        rtcEngine: _engine,
        canvas: const VideoCanvas(
          uid: 0,
          renderMode: RenderModeType.renderModeHidden,
        ),
      ),
    );
  }

  Widget _remoteVideo() {

    if (_remoteUid != null) {
      return AgoraVideoView(
        controller: VideoViewController.remote(
          rtcEngine: _engine,
          canvas: VideoCanvas(
            uid: _remoteUid,
            renderMode: RenderModeType.renderModeHidden,
          ),
          connection: RtcConnection(channelId: channelName),
        ),
      );
    } else {
      return Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF0F766E), Color(0xFF134E4A)],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircleAvatar(
                radius: 50,
                backgroundColor: Colors.white12,
                child: Icon(Icons.person, size: 50, color: Colors.white54),
              ),
              const SizedBox(height: 25),
              ScalingText(
                widget.callEnd == true
                    ? getTranslated(context, AppString.disconnect_call).toString()
                    : widget.flag == "OutGoing"
                        ? getTranslated(context, AppString.ringing).toString()
                        : getTranslated(context, AppString.connect_call).toString(),
                style: const TextStyle(fontSize: 18, color: Colors.white, fontWeight: FontWeight.w400, letterSpacing: 0.5),
              ),
            ],
          ),
        ),
      );
    }
  }
}
