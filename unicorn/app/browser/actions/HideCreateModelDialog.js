// Copyright © 2016, Numenta, Inc. Unless you have purchased from
// Numenta, Inc. a separate commercial license for this software code, the
// following terms and conditions apply:
//
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU Affero Public License version 3 as published by the
// Free Software Foundation.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU Affero Public License for more details.
//
// You should have received a copy of the GNU Affero Public License along with
// this program. If not, see http://www.gnu.org/licenses.
//
// http://numenta.org/licenses/

import {ACTIONS} from '../lib/Constants';


/**
 * Hide {@link CreateModelDialog} page
 * @param  {FluxibleContext} actionContext - The action context
 * @emits {HIDE_CREATE_MODEL_DIALOG}
 */
export default function (actionContext) {
  actionContext.getGATracker().event('ACTION',
    ACTIONS.HIDE_CREATE_MODEL_DIALOG);
  actionContext.dispatch(ACTIONS.HIDE_CREATE_MODEL_DIALOG);
}
