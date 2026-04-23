class Register {
  bool? success;
  Data? data;
  String? msg;
  String? token;
  String? refreshToken;
  String? expiresIn;

  Register({this.success, this.data, this.msg, this.token, this.refreshToken, this.expiresIn});

  Register.fromJson(Map<String, dynamic> json) {
    success = json['success'];
    data = json['data'] != null ? new Data.fromJson(json['data']) : null;
    msg = json['msg'];
    token = json['token'];
    refreshToken = json['refresh_token'];
    expiresIn = json['expires_in'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['success'] = this.success;
    if (this.data != null) {
      data['data'] = this.data!.toJson();
    }
    data['msg'] = this.msg;
    data['token'] = this.token;
    data['refresh_token'] = this.refreshToken;
    data['expires_in'] = this.expiresIn;
    return data;
  }
}

class Data {
  String? name;
  String? email;
  int? verify;
  String? phone;
  String? phoneCode;
  int? status;
  String? updatedAt;
  String? createdAt;
  int? id;
  String? uniqueId;
  String? token;
  String? image;
  String? gender;
  String? dob;
  int? otp;
  String? fullImage;
  List<Roles>? roles;

  Data({this.name, this.email, this.verify, this.phone, this.phoneCode, this.status, this.updatedAt, this.createdAt, this.id, this.uniqueId, this.token, this.image, this.gender, this.dob, this.otp, this.fullImage, this.roles});

  Data.fromJson(Map<String, dynamic> json) {
    name = json['name'];
    email = json['email'];
    verify = json['verify'];
    phone = json['phone'];
    phoneCode = json['phone_code'];
    status = json['status'];
    updatedAt = json['updated_at'];
    createdAt = json['created_at'];
    id = json['id'];
    uniqueId = json['unique_id'];
    token = json['token'];
    image = json['image'];
    gender = json['gender'];
    dob = json['dob'];
    otp = json['otp'];
    fullImage = json['fullImage'];
    if (json['roles'] != null) {
      roles = [];
      json['roles'].forEach((v) {
        roles!.add(new Roles.fromJson(v));
      });
    }
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['name'] = this.name;
    data['email'] = this.email;
    data['verify'] = this.verify;
    data['phone'] = this.phone;
    data['phone_code'] = this.phoneCode;
    data['status'] = this.status;
    data['updated_at'] = this.updatedAt;
    data['created_at'] = this.createdAt;
    data['id'] = this.id;
    data['unique_id'] = this.uniqueId;
    data['token'] = this.token;
    data['image'] = this.image;
    data['gender'] = this.gender;
    data['dob'] = this.dob;
    data['otp'] = this.otp;
    data['fullImage'] = this.fullImage;
    if (this.roles != null) {
      data['roles'] = this.roles!.map((v) => v.toJson()).toList();
    }
    return data;
  }
}

class Roles {
  int? id;
  String? name;
  String? guardName;
  String? createdAt;
  String? updatedAt;
  Pivot? pivot;

  Roles({this.id, this.name, this.guardName, this.createdAt, this.updatedAt, this.pivot});

  Roles.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    name = json['name'];
    guardName = json['guard_name'];
    createdAt = json['created_at'];
    updatedAt = json['updated_at'];
    pivot = json['pivot'] != null ? new Pivot.fromJson(json['pivot']) : null;
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['id'] = this.id;
    data['name'] = this.name;
    data['guard_name'] = this.guardName;
    data['created_at'] = this.createdAt;
    data['updated_at'] = this.updatedAt;
    if (this.pivot != null) {
      data['pivot'] = this.pivot!.toJson();
    }
    return data;
  }
}

class Pivot {
  int? modelId;
  int? roleId;
  String? modelType;

  Pivot({this.modelId, this.roleId, this.modelType});

  Pivot.fromJson(Map<String, dynamic> json) {
    modelId = json['model_id'];
    roleId = json['role_id'];
    modelType = json['model_type'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['model_id'] = this.modelId;
    data['role_id'] = this.roleId;
    data['model_type'] = this.modelType;
    return data;
  }
}
