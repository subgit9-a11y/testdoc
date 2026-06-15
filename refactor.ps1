$files = @(
    "lib/chat/pages/chat_page.dart",
    "lib/chat/pages/full_photo_page.dart",
    "lib/chat/pages/home_page.dart",
    "lib/chat/widgets/loading_view.dart"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $content = $content -replace 'ColorConstants\.greyColor2', 'Theme.of(context).colorScheme.surfaceContainerHighest'
        $content = $content -replace 'ColorConstants\.greyColor', 'Theme.of(context).colorScheme.onSurfaceVariant'
        $content = $content -replace 'ColorConstants\.themeColor', 'Theme.of(context).colorScheme.primary'
        $content = $content -replace 'ColorConstants\.primaryColor', 'Theme.of(context).colorScheme.primary'
        $content = $content -replace 'ColorConstants\.black', 'Theme.of(context).colorScheme.onSurface'
        $content = $content -replace "import '\.\./constants/colors\.dart';", ""
        $content = $content -replace "import 'package:doctro/chat/constants/colors\.dart';", ""
        Set-Content -Path $file -Value $content -NoNewline
    }
}

$pgFile = "lib/screens/paymentScreen/PaymentGateway.dart"
if (Test-Path $pgFile) {
    $content = Get-Content $pgFile -Raw
    $content = $content -replace 'color:\s*Colors\.black12', 'color: Theme.of(context).shadowColor.withOpacity(0.12)'
    Set-Content -Path $pgFile -Value $content -NoNewline
}

$cbFile = "lib/screens/appointment/cancel_appointment_backup.dart"
if (Test-Path $cbFile) {
    $content = Get-Content $cbFile -Raw
    $content = $content -replace 'Colors\.white\.withOpacity\(0\.14\)', 'Theme.of(context).colorScheme.onSurface.withOpacity(0.14)'
    $content = $content -replace 'color:\s*Colors\.white\b', 'color: Theme.of(context).colorScheme.onPrimary'
    Set-Content -Path $cbFile -Value $content -NoNewline
}

$colorsFile = "lib/chat/constants/colors.dart"
if (Test-Path $colorsFile) {
    Remove-Item $colorsFile
    Write-Host "colors.dart deleted"
}
