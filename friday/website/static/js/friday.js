/**
 * Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
 *
 * AJAX utility functions. This file requires the jQuery library.
 *
 * Created on 2010-02-11.
 * $Id$
 */


var friday = {


    // Toggles the AJAX mode in an AJAX box identified by ajax_box_id.
    // @param ajax_box_id
    toggle: function(ajax_box_id) {
        $(ajax_box_id + " .ajax-view").toggle();
        $(ajax_box_id + " .ajax-edit").toggle();
    },


    // Submits an AJAX form.
    // @param ajax_box_id
    // @param ajax_form_id
    submitAjaxForm: function(ajax_box_id, ajax_form_id) {
        var ajax_box = $(ajax_box_id);
        var ajax_form = $(ajax_form_id);
        // Prepare the AJAX request options.
        var options = {
            type: ajax_form.attr("method"),
            url: ajax_form.attr("action"),
            data: ajax_form.serialize(),
            success: function(data) {
                ajax_box.after(data).remove();
            },
            error: function(xhr, status, exc) {
                $("input[type='submit']", ajax_form).removeAttr("disabled");
                $(".ajax-error", ajax_box).show();
            }
        };
        // Before sending AJAX request...
        $("input[type='submit']", ajax_form).attr("disabled", "disabled");
        $(".ajax-error", ajax_box).hide();
        // Send AJAX request...
        $.ajax(options);
        // Return false, to disable default behavior.
        return false;
    },


    showMap: function(lat, lon, container_id) {
        var MAP_ZOOM = 16;
        if (GBrowserIsCompatible()) {
            var geo_pt = new GLatLng(lat, lon);
            var marker = new GMarker(geo_pt);
            var container = $(container_id).get(0);
            var map = new GMap2(container);
            map.addControl(new GLargeMapControl());
            map.setCenter(geo_pt, MAP_ZOOM);
            map.addOverlay(marker);
        }
    },


    findInMap: function(address, container_id, on_found, on_not_found) {
        var MAP_ZOOM = 16;
        var geocoder = new GClientGeocoder();
        if (geocoder) {
            geocoder.getLatLng(
                address,
                function(geo_pt) {
                    if (!geo_pt) {
                        on_not_found(address);
                    } else {
                        var marker = new GMarker(geo_pt, {draggable: true});
                        var container = $(container_id).get(0);
                        var map = new GMap2(container);
                        map.addControl(new GLargeMapControl());
                        map.setCenter(geo_pt, MAP_ZOOM);
                        GEvent.addListener(marker, "dragend", function(lat_lon) {
                            on_found(lat_lon.lat(), lat_lon.lng());
                        });
                        map.addOverlay(marker);
                        on_found(geo_pt.lat(), geo_pt.lng());
                    }
                }
            );
        }
    },


    dummy: function() {
        alert("dummy() called!");
        return false;
    }


}  // namespace friday




