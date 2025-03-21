# -*- coding: utf-8 -*-
# module worker.py
#
# Copyright (c) 2024  Cogniteva SAS
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ---------------------------------------------------------------------------
import logging                                    #
# ---------------------------------------------------------------------------
from cerberus import Validator, TypeDefinition

import semver
from pathlib import Path                          #
# ---------------------------------------------------------------------------
from parscival.utils.logging import logging_decorator, logging_set_context
_alias_ = 'validate.dogma'
_version_ = '1.0.0'
logging_default_context = f"|{_alias_}:{_version_}         |"
# ---------------------------------------------------------------------------
log = logging.getLogger(__name__)                 #
# ---------------------------------------------------------------------------
class DogmaValidator(Validator):
  def __init__(self, *args, **kwargs):
    super(DogmaValidator, self).__init__(*args, **kwargs)
    self.require_all = True

  def _validate_one_of_members(self, constraint, field, value):
    """ Validate that at least one specified field is present.
    The rule's arguments are validated against this schema:
    {'type': 'list', 'schema': {'type': 'string'}}
    """
    if not isinstance(constraint, list):
      self._error(field, "The 'one_of_members' rule must be a list of fields")
      return

    present_fields = None

    if value:
      present_fields = [f for f in constraint if f in value]

    if not present_fields:
      self._error(field, f"At least one of the fields {constraint} must be present")

  def _validate_type_semver(self, value):
    """ Validate that the value is a valid semantic version.
    The rule's arguments are validated against this schema:
    {'type': 'string'}
    """
    if not isinstance(value, str):
      self._error('type', 'Must be a string')
      return False

    try:
      semver.VersionInfo.parse(value)
      return True
    except ValueError:
      self._error('type', 'Must be a valid semantic version')
      return False

  def _validate_type_any(self, value):
    """ Validate that the value is a any
    {'type': 'string'}
    """

    if not isinstance(value, object):
      self._error('type', 'Must be any value')
      return False

    return True


def dogma_to_cerberus_schema(dogma_schema):
  """
  Translates a Dogma schema to a Cerberus schema.

  Args:
      dogma_schema (dict): The Dogma schema to translate.

  Returns:
      dict: The translated Cerberus schema.

  Raises:
      ValueError: If reserved words are used improperly or 'array' is not defined as a list.
  """
  # reserved keywords in Dogma
  dogma_reserved = set([
      'items', 'valuesrules', 'dict'
  ])

  # attributes recognized in Dogma schema
  dogma_attributes = set([
      'allof', 'allow_unknown', 'allowed', 'anyof', 'check_with', 'coerce',
      'contains', 'default', 'default_setter', 'dependencies', 'empty',
      'excludes', 'forbidden', 'keysrules', 'max', 'maxlength', 'meta',
      'min', 'minlength', 'noneof', 'nullable', 'oneof', 'purge_unknown',
      'readonly', 'regex', 'rename', 'rename_handler', 'require_all',
      'required', 'schema', 'type', 'one_of_members'
  ])

  def update_schema(node):
    """
    Updates the schema by renaming 'qualifier' to 'required' with the value of True if 'required'.
    """
    if isinstance(node, dict):
      new_data = {}
      for key, value in node.items():
        if key == 'qualifier' and isinstance(value, str):
          new_key = 'required'
          new_value = (value in ['required', 'required once', 'required repeated'])
          new_data[new_key] = new_value
        else:
          new_data[key] = update_schema(value)
      return new_data
    elif isinstance(node, list):
      return [update_schema(item) for item in node]
    else:
      return node

  def translate_node(node):
    """
    Recursively translates the Dogma schema nodes to Cerberus schema nodes.
    """
    if isinstance(node, dict):
      translated = {}
      for key, value in node.items():
        if key == 'one_of_members':
          pass
        if key == 'type' and isinstance(value, str) and value in dogma_reserved:
          raise ValueError(f"'type: {value}' is unknown")
        elif key in dogma_reserved:
          raise ValueError(f"Key '{key}' is reserved word")
        elif key in dogma_attributes:
          translated[key] = value
        elif key == 'members':
          if translated.get('type') == 'record':
            translated['type'] = 'dict'
            translated['schema'] = translate_node(value)
          elif translated.get('type') == 'map':
            translated['type'] = 'dict'
            translated['valuesrules'] = translate_node(value)
          elif translated.get('type') == 'array':
            # ensure 'array' are defined as a list
            if not isinstance(value, list):
              raise ValueError(
                  f"Expected 'array' to be a list, got {type(value).__name__}")
            translated['type'] = 'list'
            translated['items'] = [translate_node(item) for item in value] if isinstance(
                value, list) else translate_node(value)
          elif translated.get('type') == 'collection':
            translated['type'] = 'list'
            translated['schema'] = translate_node(value)
        else:
          translated[key] = translate_node(value)

      # handle cases where `members` is missing
      if 'type' in translated:
        type_value = translated['type']
        if type_value == 'record':
          translated['type'] = 'dict'
          if 'schema' not in translated:
            translated['schema'] = {}
        elif type_value == 'map':
          translated['type'] = 'dict'
          if 'valuesrules' not in translated:
            translated['valuesrules'] = {}
        elif type_value == 'array':
          translated['type'] = 'list'
          if 'items' not in translated:
            translated['items'] = []
        elif type_value == 'collection':
          translated['type'] = 'list'
          if 'schema' not in translated:
            translated['schema'] = {}

      return translated

  # update the schema and then translate it
  cerberus_schema = translate_node(update_schema(dogma_schema))
  return cerberus_schema

@logging_decorator(logging_default_context)
def dogma_schema_normalize(document, schema):
  # parse the dot notation schema
  try:
    schema = dogma_to_cerberus_schema(schema)
  except Exception as e:
    raise e

  # create a DogmaValidator with the parsed schema
  v = DogmaValidator(schema)

  # validate the spec against the schema
  document_normalized =  v.normalized(document)

  return document_normalized

@logging_decorator(logging_default_context)
def dogma_schema_validate(document, schema):
  # parse the dot notation schema
  try:
    schema = dogma_to_cerberus_schema(schema)
  except Exception as e:
    raise e

  try:
    # create a DogmaValidator with the parsed schema
    v = DogmaValidator(schema)
  except Exception as e:
    raise e

  # validate the spec against the schema
  if not v.validate(document):
    log.error("Schema is invalid")
    log.error(v.errors)
    return False

  return True
