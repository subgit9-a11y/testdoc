import 'package:doctro/constant/common_function.dart';
import 'package:dio/dio.dart' hide Headers;

class ServerError implements Exception {
  int? _errorCode;
  String _errorMessage = "";

  ServerError.withError({error}) {
    _handleError(error);
  }

  getErrorCode() {
    return _errorCode;
  }

  getErrorMessage() {
    return _errorMessage;
  }

  _handleError(DioException error) {
    _errorCode = error.response?.statusCode;

    if (error.response?.statusCode == 401) {
      String msg = error.response?.data['msg']?.toString() ??
          error.response?.data['message']?.toString() ??
          "Unauthorized";
      if (msg.toLowerCase().contains("unauthorized") ||
          msg.toLowerCase().contains("session")) {
        msg = "Session expired. Please log in again.";
      }
      _errorMessage = msg;
      return CommonFunction.toastMessage(msg);
    } else if (error.response?.data['error'] != null) {
      _errorMessage = '${error.response!.data['error']}';
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.badResponse) {
      if (error.response?.data['msg'] != null) {
        _errorMessage = '${error.response!.data['msg'].toString()}';
        return CommonFunction.toastMessage(_errorMessage);
      } else if (error.response?.data['message'] != null) {
        _errorMessage = '${error.response!.data['message'].toString()}';
        return CommonFunction.toastMessage(_errorMessage);
      }
    } else if (error.type == DioExceptionType.unknown) {
      _errorMessage = error.response?.data['msg']?.toString() ?? "Network error";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.cancel) {
      _errorMessage = "Request was cancelled";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.connectionError) {
      _errorMessage = "Connection failed. Please check internet connection";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.connectionTimeout) {
      _errorMessage = "Connection timeout";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.badCertificate) {
      _errorMessage = error.response?.data['msg']?.toString() ?? "Bad certificate";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.receiveTimeout) {
      _errorMessage = "Receive timeout in connection";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.type == DioExceptionType.sendTimeout) {
      _errorMessage = "Send timeout in connection";
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['name'] != null) {
      _errorMessage = error.response!.data['errors']['name'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['phone'] != null) {
      _errorMessage = error.response!.data['errors']['phone'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['phone_code'] != null) {
      _errorMessage = error.response!.data['errors']['phone_code'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['password'] != null) {
      _errorMessage = error.response!.data['errors']['password'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['email'] != null) {
      _errorMessage = error.response!.data['errors']['email'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['description'] != null) {
      _errorMessage = error.response!.data['errors']['description'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['old_password'] != null) {
      _errorMessage = error.response!.data['errors']['old_password'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    } else if (error.response?.data['errors']?['password_confirmation'] != null) {
      _errorMessage = error.response!.data['errors']['password_confirmation'][0].toString();
      return CommonFunction.toastMessage(_errorMessage);
    }
    if (_errorMessage.isEmpty) {
      _errorMessage = "Something went wrong. Please try again.";
    }
    return _errorMessage;
  }
}
