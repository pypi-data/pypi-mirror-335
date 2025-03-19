# coding: utf-8

"""
    Regula Face SDK Web API

    <a href=\"https://regulaforensics.com/products/face-recognition-sdk/  \" target=\"_blank\">Regula Face SDK</a> is a cross-platform biometric verification solution for a digital identity verification process and image quality assurance. The SDK enables convenient and reliable face capture on the client side (mobile, web, and desktop) and further processing on the client or server side.   The Face SDK includes the following features:  * <a href=\"https://docs.regulaforensics.com/develop/face-sdk/overview/introduction/#face-detection\" target=\"_blank\">Face detection and image quality assessment</a> * <a href=\"https://docs.regulaforensics.com/develop/face-sdk/overview/introduction/#face-comparison-11\" target=\"_blank\">Face match (1:1)</a> * <a href=\"https://docs.regulaforensics.com/develop/face-sdk/overview/introduction/#face-identification-1n\" target=\"_blank\">Face search (1:N)</a> * <a href=\"https://docs.regulaforensics.com/develop/face-sdk/overview/introduction/#liveness-assessment\" target=\"_blank\">Liveness detection</a>  Here is the <a href=\"https://github.com/regulaforensics/FaceSDK-web-openapi  \" target=\"_blank\">OpenAPI specification on GitHub</a>.   ### Clients * [JavaScript](https://github.com/regulaforensics/FaceSDK-web-js-client) client for the browser and node.js based on axios * [Java](https://github.com/regulaforensics/FaceSDK-web-java-client) client compatible with jvm and android * [Python](https://github.com/regulaforensics/FaceSDK-web-python-client) 3.5+ client * [C#](https://github.com/regulaforensics/FaceSDK-web-csharp-client) client for .NET & .NET Core   # noqa: E501

    The version of the OpenAPI document: 6.2.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from regula.facesdk.webclient.gen.configuration import Configuration


class TransactionInfo(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'code': 'int',
        'status': 'int',
        'tag': 'str',
        'transaction_id': 'str',
        'video': 'str',
        'age': '[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]',
        'portrait': 'str',
        'metadata': '{str: (bool, date, datetime, dict, float, int, list, str, none_type)}',
        'type': 'LivenessType',
    }

    attribute_map = {
        'code': 'code',
        'status': 'status',
        'tag': 'tag',
        'transaction_id': 'transactionId',
        'video': 'video',
        'age': 'age',
        'portrait': 'portrait',
        'metadata': 'metadata',
        'type': 'type',
    }

    def __init__(self, code=None, status=None, tag=None, transaction_id=None, video=None, age=None, portrait=None, metadata=None, type=None, local_vars_configuration=None):  # noqa: E501
        """TransactionInfo - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._code = None
        self._status = None
        self._tag = None
        self._transaction_id = None
        self._video = None
        self._age = None
        self._portrait = None
        self._metadata = None
        self._type = None
        self.discriminator = None

        if code is not None:
            self.code = code
        if status is not None:
            self.status = status
        if tag is not None:
            self.tag = tag
        if transaction_id is not None:
            self.transaction_id = transaction_id
        if video is not None:
            self.video = video
        if age is not None:
            self.age = age
        if portrait is not None:
            self.portrait = portrait
        if metadata is not None:
            self.metadata = metadata
        if type is not None:
            self.type = type

    @property
    def code(self):
        """Gets the code of this TransactionInfo.  # noqa: E501

        Result code, see the [FaceSDKResultCode enum](https://docs.regulaforensics.com/develop/face-sdk/web-service/development/enums/face-sdk-result-code/).  # noqa: E501

        :return: The code of this TransactionInfo.  # noqa: E501
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this TransactionInfo.

        Result code, see the [FaceSDKResultCode enum](https://docs.regulaforensics.com/develop/face-sdk/web-service/development/enums/face-sdk-result-code/).  # noqa: E501

        :param code: The code of this TransactionInfo.  # noqa: E501
        :type code: int
        """

        self._code = code

    @property
    def status(self):
        """Gets the status of this TransactionInfo.  # noqa: E501

        Whether the liveness detection is confirmed `0` or not `1`.  # noqa: E501

        :return: The status of this TransactionInfo.  # noqa: E501
        :rtype: int
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this TransactionInfo.

        Whether the liveness detection is confirmed `0` or not `1`.  # noqa: E501

        :param status: The status of this TransactionInfo.  # noqa: E501
        :type status: int
        """

        self._status = status

    @property
    def tag(self):
        """Gets the tag of this TransactionInfo.  # noqa: E501

        Session identificator, should be unique for each session.  # noqa: E501

        :return: The tag of this TransactionInfo.  # noqa: E501
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this TransactionInfo.

        Session identificator, should be unique for each session.  # noqa: E501

        :param tag: The tag of this TransactionInfo.  # noqa: E501
        :type tag: str
        """

        self._tag = tag

    @property
    def transaction_id(self):
        """Gets the transaction_id of this TransactionInfo.  # noqa: E501

        Transaction ID, there can be several transactions within one session.  # noqa: E501

        :return: The transaction_id of this TransactionInfo.  # noqa: E501
        :rtype: str
        """
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        """Sets the transaction_id of this TransactionInfo.

        Transaction ID, there can be several transactions within one session.  # noqa: E501

        :param transaction_id: The transaction_id of this TransactionInfo.  # noqa: E501
        :type transaction_id: str
        """

        self._transaction_id = transaction_id

    @property
    def video(self):
        """Gets the video of this TransactionInfo.  # noqa: E501

        Link to the session video, depends on the selected storage type. [Learn more](https://docs.regulaforensics.com/develop/face-sdk/web-service/administration/storage/)  # noqa: E501

        :return: The video of this TransactionInfo.  # noqa: E501
        :rtype: str
        """
        return self._video

    @video.setter
    def video(self, video):
        """Sets the video of this TransactionInfo.

        Link to the session video, depends on the selected storage type. [Learn more](https://docs.regulaforensics.com/develop/face-sdk/web-service/administration/storage/)  # noqa: E501

        :param video: The video of this TransactionInfo.  # noqa: E501
        :type video: str
        """

        self._video = video

    @property
    def age(self):
        """Gets the age of this TransactionInfo.  # noqa: E501

        Approximate age with an accuracy of +/-3 years.  # noqa: E501

        :return: The age of this TransactionInfo.  # noqa: E501
        :rtype: [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]
        """
        return self._age

    @age.setter
    def age(self, age):
        """Sets the age of this TransactionInfo.

        Approximate age with an accuracy of +/-3 years.  # noqa: E501

        :param age: The age of this TransactionInfo.  # noqa: E501
        :type age: [{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]
        """

        self._age = age

    @property
    def portrait(self):
        """Gets the portrait of this TransactionInfo.  # noqa: E501

        Link to the portrait, depends on the selected storage type. [Learn more](https://docs.regulaforensics.com/develop/face-sdk/web-service/administration/storage/)  # noqa: E501

        :return: The portrait of this TransactionInfo.  # noqa: E501
        :rtype: str
        """
        return self._portrait

    @portrait.setter
    def portrait(self, portrait):
        """Sets the portrait of this TransactionInfo.

        Link to the portrait, depends on the selected storage type. [Learn more](https://docs.regulaforensics.com/develop/face-sdk/web-service/administration/storage/)  # noqa: E501

        :param portrait: The portrait of this TransactionInfo.  # noqa: E501
        :type portrait: str
        """

        self._portrait = portrait

    @property
    def metadata(self):
        """Gets the metadata of this TransactionInfo.  # noqa: E501

        A free-form object containing person's extended attributes.  # noqa: E501

        :return: The metadata of this TransactionInfo.  # noqa: E501
        :rtype: {str: (bool, date, datetime, dict, float, int, list, str, none_type)}
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this TransactionInfo.

        A free-form object containing person's extended attributes.  # noqa: E501

        :param metadata: The metadata of this TransactionInfo.  # noqa: E501
        :type metadata: {str: (bool, date, datetime, dict, float, int, list, str, none_type)}
        """

        self._metadata = metadata

    @property
    def type(self):
        """Gets the type of this TransactionInfo.  # noqa: E501


        :return: The type of this TransactionInfo.  # noqa: E501
        :rtype: LivenessType
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this TransactionInfo.


        :param type: The type of this TransactionInfo.  # noqa: E501
        :type type: LivenessType
        """

        self._type = type

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TransactionInfo):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TransactionInfo):
            return True

        return self.to_dict() != other.to_dict()
