#!/usr/bin/python
# ===============================================================================
# Copyright (C) 2013 Darren Poulson
#
# This file is part of R2_Control.
#
# R2_Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# R2_Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with R2_Control.  If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================

from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
from flask import Blueprint, request
from .ServoControl import ServoControl
standard_library.install_aliases()


def construct_blueprint(name):

    api = Blueprint('servo_' + name, __name__)

    _servo = ServoControl(name)

    @api.route('/', methods=['GET'])
    @api.route('/list', methods=['GET'])
    def _servo_list():
        """GET to list all current servos and position"""
        message = ""
        if request.method == 'GET':
            message += _servo.list_servos()
        return message

    @api.route('/<servo_name>/<servo_position>/<servo_duration>', methods=['GET'])
    def _servo_move(servo_name, servo_position, servo_duration):
        """GET will move a selected servo to the required position over a set duration"""
        if request.method == 'GET':
            _servo.servo_command(servo_name, servo_position, servo_duration)
        return "Ok"

    @api.route('/close/<duration>', methods=['GET'])
    def _servo_close_slow(duration):
        """GET to close all dome servos slowly"""
        if request.method == 'GET':
            _servo.close_all_servos(duration)
            return "Ok"
        return "Fail"

    @api.route('/close', methods=['GET'])
    def _servo_close():
        """GET to close all servos"""
        if request.method == 'GET':
            _servo.close_all_servos(0)
            return "Ok"
        return "Fail"

    @api.route('/open', methods=['GET'])
    def _servo_open():
        """GET to open all servos"""
        if request.method == 'GET':
            _servo.open_all_servos(0)
            return "Ok"
        return "Fail"

    @api.route('/open/<duration>', methods=['GET'])
    def _servo_open_slow(duration):
        """GET to open all dome servos slowly"""
        if request.method == 'GET':
            _servo.open_all_servos(duration)
            return "Ok"
        return "Fail"

    return(api)
