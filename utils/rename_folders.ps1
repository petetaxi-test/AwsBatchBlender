# Note: only works if all your scenes have unique names
$renderOutputDir = "~/rendering/finished_renders"

$directories = Get-ChildItem -Path "$renderOutputDir" -Directory

foreach($directory in $directories) {
    $name = $directory | Select-Object -ExpandProperty Name

    if ($name -match '[^-]*-(?<Stub>[^-]*)-.*') {
        $stub = $Matches.Stub

        $source = "${renderOutputDir}/${name}"
        $target = "${renderOutputDir}/${stub}"

        "${source} --> ${target}"
        mv "${source}" "${target}"
    }
}