# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""
Implements Unicorn's model interface.
"""


from datetime import datetime
import json
import logging
from optparse import OptionParser
import pkg_resources
import sys

import validictory

from nupic.data import fieldmeta
from nupic.frameworks.opf.modelfactory import ModelFactory


# TODO: can we reuse htmengine primitives here?
from htmengine.algorithms.modelSelection.clusterParams import (
  getScalarMetricWithTimeOfDayParams)


g_log = logging.getLogger(__name__)



class _Options(object):
  """Options returned by _parseArgs"""


  __slots__ = ("modelId", "stats",)


  def __init__(self, modelId, stats):
    """
    :param str modelId: model identifier
    :param dict stats: Metric data stats per engine/stats_schema.json.
    """
    self.modelId = modelId
    self.stats = stats



def _parseArgs():
  """ Parse command-line args

  :rtype: _Options object
  """
  helpString = (
    "%prog [options]\n\n"
    "Start Unicorn Engine that runs a single model.")

  parser = OptionParser(helpString)

  parser.add_option(
    "--model",
    action="store",
    type="string",
    dest="modelId",
    help="Required: Model id string")

  parser.add_option(
    "--stats",
    action="store",
    type="string",
    dest="stats",
    help=("Required: see engine/stats_schema.json"))


  options, positionalArgs = parser.parse_args()

  if len(positionalArgs) != 0:
    parser.error("Command accepts no positional args")

  if not options.modelId:
    parser.error("Missing or empty --modelId option value")

  if not options.stats:
    parser.error("Missing or empty --stats option value")

  stats = json.loads(options.stats)

  try:
    validictory.validate(
      stats,
      json.load(pkg_resources.resource_stream(__name__, "stats_schema.json")))
  except validictory.ValidationError as ex:
    parser.error("--stats option value failed schema validation: %r" % (ex,))


  return _Options(modelId=options.modelId, stats=stats)



class _Anomalizer(object):
  """ This class is responsible for anomaly likelihood processing. Its instance
  maintains a buffer of results (of the necessary window size) and anomaly state
  in memory.

  NOTE: consider modifying htmengine's anomaly_likelihood_helper.py so that we
  can share it with htmengine's Anomaly Service


  TODO Flesh me out
  """

  def process(self, timestamp, metricValue, rawAnomalyScore):
    """ Perform anomaly likelihood processing

    :param datetime.datetime timestamp: metric data sample's timestamp
    :param number metricValue: scalar value of metric data sample; float or int
    :param float rawAnomalyScore: raw anomaly score computed by NuPIC model

    :returns: anomaly likelihood value
    :rtype: float
    """
    pass



class _ModelRunner(object):
  """ Use OPF Model to process metric data samples from stdin and and emit
  anomaly likelihood results to stdout
  """

  # Input column meta info compatible with parameters generated by
  # getScalarMetricWithTimeOfDayParams
  # of htmengine.algorithms.selection.clusterParams
  _INPUT_RECORD_SCHEMA = (
    fieldmeta.FieldMetaInfo("c0", fieldmeta.FieldMetaType.datetime,
                            fieldmeta.FieldMetaSpecial.timestamp),
    fieldmeta.FieldMetaInfo("c1", fieldmeta.FieldMetaType.float,
                            fieldmeta.FieldMetaSpecial.none),
  )


  def __init__(self, modelId, stats):
    """
    :param str modelId: model identifier
    :param dict stats: Metric data stats per engine/stats_schema.json.
    """
    self._modelId = modelId
    self._model = self._createModel(stats=stats)
    self._anomalizer = _Anomalizer()


  @classmethod
  def _createModel(cls, stats):
    """Instantiate and configure an OPF model

    :param dict stats: Metric data stats per engine/stats_schema.json.
    :returns: OPF Model instance
    """
    # Generate swarm params
    possibleModels = getScalarMetricWithTimeOfDayParams(
      metricData=[0],
      minVal=stats["min"],
      maxVal=stats["max"],
      minResolution=stats.get("minResolution"))

    swarmParams = possibleModels[0]

    model = ModelFactory.create(modelConfig=swarmParams["modelConfig"])
    model.enableLearning()
    model.enableInference(swarmParams["inferenceArgs"])


  @classmethod
  def _readInputMessages(cls):
    """Create a generator that waits for and yields next input message from
    stdin

    yields two-tuple (<timestamp>, <scalar-value>), where <timestamp> is the
    `datetime.datetime` timestamp of the metric data sample and <scalar-value>
    is the floating point value of the metric data sample.
    """
    while True:
      message = sys.stdin.readline()

      if message:
        timestamp, scalarValue = json.loads(message)
        yield (datetime.utcfromtimestamp(timestamp), scalarValue)
      else:
        # Front End closed the pipe (or died)
        break


  @classmethod
  def _emitOutputMessage(cls, rowIndex, anomalyLikelihood):
    """Emit output message to stdout

    :param int rowIndex: 0-based index of corresponding input sample
    :param float anomalyLikelihood: computed anomaly likelihood value
    """
    message = "%s\n" % (json.dumps([rowIndex, anomalyLikelihood]),)

    sys.stdout.write(message)
    sys.stdout.flush()


  def _computeAnomalyLikelihood(self, inputRow):
    """ Compute anomaly likelihood

    :param tuple inputRow: Two-tuple input metric data row
      (<datetime-timestamp>, <float-scalar>)

    :returns: Anomaly likelihood
    :rtype: float
    """
    # Generate raw anomaly score
    # TODO: opfModelInputRecordFromSequence doesn't exist yet
    inputRecord = opfModelInputRecordFromSequence(inputRow,
                                                  self._INPUT_RECORD_SCHEMA)
    rawAnomalyScore = self._model.run(inputRecord).inferences["anomalyScore"]

    # Generate anomaly likelihood
    return self._anomalizer.process(
      timestamp=inputRow[0],
      metricValue=inputRow[1],
      rawAnomalyScore=rawAnomalyScore)


  def run(self):
    """ Run the model: ingest and process the input metric data and emit output
    messages containing anomaly scores
    """
    g_log.info("Processing model=%s", self._modelId)

    for rowIndex, inputRow in enumerate(self._readInputMessages()):
      anomalyLikelihood = self._computeAnomalyLikelihood(inputRow)

      self._emitOutputMessage(rowIndex=rowIndex,
                              anomalyLikelihood=anomalyLikelihood)



def main():
  try:

    options = _parseArgs()

    _ModelRunner(modelId=options.modelId, stats=options.stats).run()

  except Exception as ex:  # pylint: disable=W0703
    g_log.exception("Engine failed")

    try:
      # Preserve the original exception context
      raise
    finally:

      errorMessage = {
        "errorText": str(ex) or repr(ex),
        "diagnosticInfo": repr(ex)
      }

      errorMessage = "%s\n" % (json.dumps(errorMessage))

      try:
        sys.stderr.write(errorMessage)
      except Exception:  # pylint: disable=W0703
        g_log.exception("Failed to emit error message to stderr; msg=%s",
                        errorMessage)



if __name__ == "__main__":
  main()
