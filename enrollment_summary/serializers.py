from rest_framework import serializers

class EnrollmentSummarySerializer(serializers.Serializer):
    course_key = serializers.CharField()
    course_title = serializers.CharField()
    enrollment_status = serializers.CharField()
    graded_subsections_count = serializers.IntegerField()

    def to_representation(self, obj):
        titles = self.context.get("course_titles", {})
        graded_counts = self.context.get("graded_counts", {})
        course_key = str(getattr(obj, "course_id"))
        return {
            "course_key": course_key,
            "course_title": titles.get(course_key, "Unknown"),
            "enrollment_status": "active" if getattr(obj, "is_active", False) else "inactive",
            "graded_subsections_count": int(graded_counts.get(course_key, 0)),
        }
